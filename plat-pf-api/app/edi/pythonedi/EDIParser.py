"""
Parses a provided EDI message and tries to build a dictionary from the data
Provides hints if data is missing, incomplete, or incorrect.
"""

import datetime
import re

from .supported_formats import supported_formats
from .debug import Debug


class EDIParser(object):
    def __init__(self, edi_format=None, element_delimiter="^", segment_delimiter="\n", data_delimiter="`"):
        # Set default delimiters
        self.element_delimiter = element_delimiter
        self.segment_delimiter = segment_delimiter
        self.data_delimiter = data_delimiter

        # Set EDI format to use
        if edi_format in supported_formats:
            self.edi_format = supported_formats[edi_format]
        elif edi_format is None:
            self.edi_format = None
        else:
            raise ValueError("Unsupported EDI format {}".format(edi_format))

    def get_group_control_header(self, content):
        segment = []
        try:
            index = content.index('ST*')
            segment = content[0:index]
            content = content[index:-1]
        except Exception as ex:
            Debug.explain(str(ex))
        return segment, content

    def get_group_control_trailer(self, content):
        segment = []
        try:
            index = content.index('GE*')
            segment = content[index:-1]
            content = content[0:index]
        except Exception as ex:
            Debug.explain(str(ex))
        return segment, content

    def parser_content_edi(self, content: str):
        assert content is not None, "Content EDI is not None"
        edi_structure = {}
        try:
            control_group_header, content = self.get_group_control_header(content)
            group_control_trailer, content = self.get_group_control_trailer(content)
            #
            st_keys = re.findall(r'ST[*^]\d{3}[*^]\d{4}.', content)
            last_st_index = len(st_keys) - 1
            edi_content = {
                st_keys[i]: content[content.index(st_keys[i]): content.index(st_keys[i + 1])] if i < last_st_index else
                content[content.index(st_keys[i]): -1] for i in range(len(st_keys))}
            edi_structure['control_group_header'] = control_group_header
            edi_structure['edi_details'] = edi_content
            edi_structure['group_control_trailer'] = group_control_trailer
        except Exception as ex:
            Debug.explain(str(ex))
        return edi_structure

    def parse(self, data):
        """ Processes each line in the string `data`, attempting to auto-detect the EDI type.

        Returns the parsed message as a dict. """

        parser_content_edi = self.parser_content_edi(data)

        edi_details = parser_content_edi['edi_details']

        to_returns = []
        found_segments = []

        for st_key, edi in edi_details.items():

            details = edi.split('IT1*')
            header = details[0]
            del details[0]

            # summary = edi[t[-1], edi[-1]]
            for detail in details:
                # Break the message up into chunks
                edi = header + 'IT1*' + detail
                edi_segments = edi.split(self.segment_delimiter)

                # Eventually, find the ST header and parse the EDI format
                if self.edi_format is None:
                    raise NotImplementedError("EDI format autodetection not built yet. Please specify an EDI format.")

                to_return = {}
                found_segment = []

                # clean last character before parser line
                edi_segments = list(
                    map(lambda x: x.strip()[:-1] if len(x.strip()) > 0 and x.strip()[-1] in ['.', '~'] else x.strip(),
                        edi_segments))

                while len(edi_segments) > 0:
                    segment = edi_segments[0]
                    if segment == "":
                        edi_segments = edi_segments[1:]
                        continue  # Line is blank, skip
                    # Capture current segment name
                    segment_name = segment.split(self.element_delimiter)[0]
                    segment_obj = None
                    # Find corresponding segment/loop format
                    for seg_format in self.edi_format:
                        # Check if segment is just a segment, a repeating segment, or part of a loop
                        if seg_format["id"] == segment_name and seg_format["max_uses"] == 1:
                            # Found a segment
                            segment_obj = self.parse_segment(segment, seg_format)
                            edi_segments = edi_segments[1:]
                            break
                        elif seg_format["id"] == segment_name and seg_format["max_uses"] > 1:
                            # Found a repeating segment
                            segment_obj, edi_segments = self.parse_repeating_segment(edi_segments, seg_format)
                            break
                        elif seg_format["id"] == "L_" + segment_name:
                            # Found a loop
                            segment_name = seg_format["id"]
                            segment_obj, edi_segments = self.parse_loop(edi_segments, seg_format)
                            break

                    if segment_obj is None:
                        Debug.log_error("Unrecognized segment: {}".format(segment))
                        edi_segments = edi_segments[1:]  # Skipping segment
                        continue
                        # raise ValueError

                    found_segment.append(segment_name)
                    to_return[segment_name] = segment_obj
                if len(found_segment) > 0:
                    found_segments.append(found_segment)
                if len(to_return) > 0:
                    to_returns.append(to_return)
        return found_segments, to_returns

    def parse_segment(self, segment, segment_format):
        """ Parse a segment into a dict according to field IDs """
        fields = segment.split(self.element_delimiter)
        if fields[0] != segment_format["id"]:
            raise TypeError(
                "Segment type {} does not match provided segment format {}".format(fields[0], segment_format["id"]))

        to_return = {}
        for field, element in zip(fields[1:], segment_format["elements"]):  # Skip the segment name field
            key = element["id"]
            value = {}
            if element["data_type"] == "DT":
                if len(field) == 8:
                    value = datetime.datetime.strptime(field, "%Y%m%d")
                elif len(field) == 6:
                    value = datetime.datetime.strptime(field, "%y%m%d")
                else:
                    value = field
            elif element["data_type"] == "TM":
                if len(field) == 4:
                    value = datetime.datetime.strptime(field, "%H%M")
                elif len(field) == 6:
                    value = datetime.datetime.strptime(field, "%H%M%S")
            elif element["data_type"] == "N0" and field != "":
                value = int(field)
            elif element["data_type"].startswith("N") and field != "":
                value = float(field) / (10 ** int(element["data_type"][-1]))
            elif element["data_type"] == "R" and field != "":
                value = float(field)
            else:
                value = field
            to_return[key] = value

        return to_return

    def parse_repeating_segment(self, edi_segments, segment_format):
        """ Parse all instances of this segment, and return any remaining segments with the seg_list """
        seg_list = []

        while len(edi_segments) > 0:
            segment = edi_segments[0]
            segment_name = segment.split(self.element_delimiter)[0]
            if segment_name != segment_format["id"]:
                break
            seg_list.append(self.parse_segment(segment, segment_format))
            edi_segments = edi_segments[1:]

        return seg_list, edi_segments

    def parse_loop(self, edi_segments, loop_format):
        """ Parse all segments that are part of this loop, and return any remaining segments with the loop_list """
        loop_list = []
        loop_dict = {}

        while len(edi_segments) > 0:
            segment = edi_segments[0]
            segment_name = segment.split(self.element_delimiter)[0]
            segment_obj = None

            # Find corresponding segment/loop format
            for seg_format in loop_format["segments"]:
                # Check if segment is just a segment, a repeating segment, or part of a loop
                if seg_format["id"] == segment_name and seg_format["max_uses"] == 1:
                    # Found a segment
                    segment_obj = self.parse_segment(segment, seg_format)
                    edi_segments = edi_segments[1:]
                elif seg_format["id"] == segment_name and seg_format["max_uses"] > 1:
                    # Found a repeating segment
                    segment_obj, edi_segments = self.parse_repeating_segment(edi_segments, seg_format)
                elif seg_format["id"] == "L_" + segment_name:
                    # Found a loop
                    segment_name = seg_format["id"]
                    segment_obj, edi_segments = self.parse_loop(edi_segments, seg_format)
            # print(segment_name, segment_obj)
            if segment_obj is None:
                # Reached the end of valid segments; return what we have
                break
            elif segment_name == loop_format["segments"][0]["id"] and loop_dict != {}:
                # Beginning a new loop, tie off this one and start fresh
                loop_list.append(loop_dict.copy())
                loop_dict = {}
            loop_dict[segment_name] = segment_obj
        if loop_dict != {}:
            loop_list.append(loop_dict.copy())
        return loop_list, edi_segments
