#
#   Copyright 2017 Gabriel Cebrian
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import os
import os.path
import re

def parse_file(filename, use_perf):
    """Parses a result file and returns a dictionary with the values of the
    summary (encoding time, and bitrate and psnr per slice type).

    Keyword arguments:
    filename -- Path of the file to parse.
    use_perf -- Boolean parameter to use perf timing values instead of the ones
            reported in the result files.
    """
    # This constant RE represents any number without thousands separator.
    NUMBER = '(?:[-+]?\d*[,.]\d+|[-+]?\d+)'

    results = dict()

    re_rd = re.compile('^\s*{}\s*([aipb])\s+({})\s+({})\s+({})\s+({})\s+({})$'
            .replace('{}', NUMBER))
    re_time = re.compile('^ Total Time:\s*({}) sec.$'
            .replace('{}', NUMBER))
    if use_perf:
        re_perf_frequency = re.compile('.*#\s*({})\s*.?Hz.*$'
                .replace('{}', NUMBER))
        re_perf_time = re.compile('^\s*({})\s*seconds time elapsed'
                .replace('{}', NUMBER))

    file = open(filename, 'r')

    for line in file:
        match = re_rd.search(line)
        if match:
            slice_type = match.group(1)
            if 'rd' not in results:
                results['rd'] = dict()
            results['rd'][slice_type] = dict()
            try:
                results['rd'][slice_type]['bitrate'] = float(match.group(2))
                results['rd'][slice_type]['y_psnr'] = float(match.group(3))
                results['rd'][slice_type]['u_psnr'] = float(match.group(4))
                results['rd'][slice_type]['v_psnr'] = float(match.group(5))
                results['rd'][slice_type]['yuv_psnr'] = float(match.group(6))
            except:
                results['rd'].pop(slice_type, None)
                if not results['rd']:
                    results.pop('rd', None)
            continue
        match = re_time.search(line)
        if match:
            try:
                results['time'] = float(match.group(1))
            except:
                pass
            continue
        if use_perf:
            match = re_perf_frequency.search(line)
            if match:
                if 'perf' not in results:
                    results['perf'] = dict()
                try:
                    results['perf']['frequency'] = float(match.group(1).replace(',', '.'))
                except:
                    if not results['perf']:
                        results.pop('perf', None)
                continue
            match = re_perf_time.search(line)
            if match:
                if 'perf' not in results:
                    results['perf'] = dict()
                try:
                    results['perf']['time'] = float(match.group(1).replace(',', '.'))
                except:
                    if not results['perf']:
                        results.pop('perf', None)
                continue

    file.close()

    return results

def parse_dir(path, pattern, use_perf):
    """Parses the result files contained in a directory and returns a dictionary
    with the values of the summary (encoding time, and bitrate and psnr per
    slice type).

    Keyword arguments:
    path -- Path of the directory.
    pattern -- Pattern of the filename used to determine the sequence name and
            the identifier.
    use_perf -- Boolean parameter to use perf timing values instead of the ones
            reported in the result files.
    """
    SEQUENCE = '(?P<sequence>.+)'
    SEQUENCE_ID = '(?P<sequence_id>\d+)'

    results = dict()

    re_filename = re.compile(pattern.replace('*', '.*')
            .replace('/n', SEQUENCE)
            .replace('/p', SEQUENCE_ID))

    for filename in os.listdir(path):
        file = os.path.join(path, filename)

        if not os.path.isfile(file):
            continue

        match = re_filename.search(filename)
        if not match:
            continue

        sequence = match.group('sequence')
        sequence_id = match.group('sequence_id')

        if sequence not in results:
            results[sequence] = dict()

        results[sequence][sequence_id] = parse_file(file, use_perf)

    return results
