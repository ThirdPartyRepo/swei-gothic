#!/usr/bin/env python3
#encoding=utf-8

from . import spline_util
from . import Rule
import math

# RULE # 11
# check inside curve
# PS: 因為 array size change, so need redo.
class Rule(Rule.Rule):
    def __init__(self):
        pass

    def apply(self, spline_dict, resume_idx, inside_stroke_dict,skip_coordinate):
        redo_travel=False

        # 最大的角度值，超過就skip
        ALMOST_LINE_RATE = 1.84

        # default: 1.75
        SLIDE_1_PERCENT_MIN = 0.8
        SLIDE_1_PERCENT_MAX = ALMOST_LINE_RATE

        MIN_DISTANCE = 12

        # clone
        format_dict_array=[]
        format_dict_array = spline_dict['dots'][1:]
        format_dict_array = self.caculate_distance(format_dict_array)

        nodes_length = len(format_dict_array)
        #print("orig nodes_length:", len(spline_dict['dots']))
        #print("format nodes_length:", nodes_length)
        #print("resume_idx:", resume_idx)

        rule_need_lines = 3
        fail_code = -1
        if nodes_length >= rule_need_lines:
            for idx in range(nodes_length):
                if idx <= resume_idx:
                    # skip traveled nodes.
                    continue

                if [format_dict_array[idx]['x'],format_dict_array[idx]['y']] in skip_coordinate:
                    continue

                # 要轉換的原來的角，第4點，不能就是我們產生出來的曲線結束點。
                # for case.3122 上面的點。
                if [format_dict_array[(idx+2)%nodes_length]['x'],format_dict_array[(idx+2)%nodes_length]['y']] in skip_coordinate:
                    continue

                is_debug_mode = False
                #is_debug_mode = True

                if is_debug_mode:
                    debug_coordinate_list = [[228,679]]
                    if not([format_dict_array[idx]['x'],format_dict_array[idx]['y']] in debug_coordinate_list):
                        continue

                    print("="*30)
                    print("index:", idx)
                    for debug_idx in range(8):
                        print(debug_idx-2,": #11 val:",format_dict_array[(idx+debug_idx+nodes_length-2)%nodes_length]['code'],'-(',format_dict_array[(idx+debug_idx+nodes_length-2)%nodes_length]['distance'],')')


                is_match_pattern = False


                x0 = format_dict_array[(idx+0)%nodes_length]['x']
                y0 = format_dict_array[(idx+0)%nodes_length]['y']
                x1 = format_dict_array[(idx+1)%nodes_length]['x']
                y1 = format_dict_array[(idx+1)%nodes_length]['y']
                x2 = format_dict_array[(idx+2)%nodes_length]['x']
                y2 = format_dict_array[(idx+2)%nodes_length]['y']

                # use more close coordinate.
                if format_dict_array[(idx+0)%nodes_length]['code']=='c':
                    x0 = format_dict_array[(idx+0)%nodes_length]['x2']
                    y0 = format_dict_array[(idx+0)%nodes_length]['y2']
                if format_dict_array[(idx+2)%nodes_length]['code']=='c':
                    x2 = format_dict_array[(idx+2)%nodes_length]['x1']
                    y2 = format_dict_array[(idx+2)%nodes_length]['y1']

                previous_x,previous_y=0,0
                next_x,next_y=0,0

                # match ?l?
                if format_dict_array[(idx+1)%nodes_length]['t'] == 'l':
                    fail_code = 100
                    is_match_pattern = True

                # match ??l
                if format_dict_array[(idx+2)%nodes_length]['t'] == 'l':
                    fail_code = 110
                    is_match_pattern = True

                # compare distance, muse large than our "large round"
                if is_match_pattern:
                    fail_code = 200
                    is_match_pattern = False
                    if format_dict_array[(idx+0)%nodes_length]['distance'] >= MIN_DISTANCE:
                        if format_dict_array[(idx+1)%nodes_length]['distance'] >= MIN_DISTANCE:
                            is_match_pattern = True

                previous_x,previous_y=0,0
                next_x,next_y=0,0

                # skip small angle
                if is_match_pattern:
                    fail_code = 300
                    is_match_pattern = False

                    # PS: 使用結束 x,y，會造成更誤判，因為沒有另外儲存 rule#99 處理記錄，會造成重覆套用。
                    #slide_percent_1 = spline_util.slide_percent(format_dict_array[(idx+0)%nodes_length]['x'],format_dict_array[(idx+0)%nodes_length]['y'],format_dict_array[(idx+1)%nodes_length]['x'],format_dict_array[(idx+1)%nodes_length]['y'],format_dict_array[(idx+2)%nodes_length]['x'],format_dict_array[(idx+2)%nodes_length]['y'])
                    slide_percent_1 = spline_util.slide_percent(x0,y0,x1,y1,x2,y2)

                    if is_debug_mode:
                            print("slide_percent 1:", slide_percent_1)
                            print("data end:",format_dict_array[(idx+0)%nodes_length]['x'],format_dict_array[(idx+0)%nodes_length]['y'],format_dict_array[(idx+1)%nodes_length]['x'],format_dict_array[(idx+1)%nodes_length]['y'],format_dict_array[(idx+2)%nodes_length]['x'],format_dict_array[(idx+2)%nodes_length]['y'])
                            print("data virtual:",x0,y0,x1,y1,x2,y2)
                            print("SLIDE_1_PERCENT_MIN:", SLIDE_1_PERCENT_MIN)
                            print("SLIDE_1_PERCENT_MAX:", SLIDE_1_PERCENT_MAX)
        
                    if slide_percent_1 >= SLIDE_1_PERCENT_MIN and slide_percent_1 <= SLIDE_1_PERCENT_MAX:
                        is_match_pattern = True

                # check black stroke in white area. @_@;
                is_apply_large_corner = False
                if is_match_pattern:
                    inside_stroke_flag,inside_stroke_dict = self.test_inside_coner(x0, y0, x1, y1, x2, y2, self.config.STROKE_MIN, inside_stroke_dict)
                    if inside_stroke_flag:
                        is_apply_large_corner = True
                        #print("match is_apply_large_corner:",x1,y1)

                if not is_apply_large_corner:
                    if is_match_pattern:
                        fail_code = 400
                        is_match_pattern = False
                        
                        join_line_debug_mode = False      # online
                        #join_line_debug_mode = True       # debug
                        join_flag = self.join_line_check(x0,y0,x1,y1,x2,y2,debug_mode=join_line_debug_mode)
                        join_flag_1 = join_flag
                        join_flag_2 = None
                        if not join_flag:
                            join_flag = self.join_line_check(x2,y2,x1,y1,x0,y0)
                            join_flag_2 = join_flag

                        if is_debug_mode:
                            print("check1_flag:",join_flag_1, "data:", x0,y0,x1,y1,x2,y2)
                            print("check2_flag:",join_flag_2, "data:", x2,y2,x1,y1,x0,y0)
                            print("final join flag:", join_flag)
                        
                        if not join_flag:
                            #print("match small coner")
                            #print(idx,"small rule5:",format_dict_array[idx]['code'])
                            is_match_pattern = True
                            #is_apply_small_corner = True
                            #pass


                if is_debug_mode:
                    if not is_match_pattern:
                        print(idx,"debug fail_code #11:", fail_code)
                    else:
                        print("match rule #11:",idx)

                if is_match_pattern:
                    #print("match rule #11")
                    #print(idx,"debug rule11+0:",format_dict_array[idx]['code'])
                    #print(idx,"debug rule11+1:",format_dict_array[(idx+1)%nodes_length]['code'])
                    #print(idx,"debug rule11+2:",format_dict_array[(idx+2)%nodes_length]['code'])

                    # make coner curve
                    round_offset = self.config.OUTSIDE_ROUND_OFFSET
                    # large curve, use small angle.
                    # start to resize round offset size.
                    resize_round_angle = 1.30
                    if slide_percent_1 >= resize_round_angle:
                        slide_percent_diff = 2.0 - slide_percent_1
                        slide_percent_total = 2.0 - slide_percent_diff
                        slide_percent_diff_percent = slide_percent_diff/slide_percent_total
                        round_offset_diff = self.config.OUTSIDE_ROUND_OFFSET - self.config.ROUND_OFFSET
                        round_offset_diff_added = int(round_offset_diff * slide_percent_diff_percent)
                        round_offset = self.config.ROUND_OFFSET + round_offset_diff_added

                    if not is_apply_large_corner:
                        round_offset = self.config.INSIDE_ROUND_OFFSET

                    format_dict_array, previous_x, previous_y, next_x, next_y = self.make_coner_curve(round_offset,format_dict_array,idx)

                    # cache transformed nodes.
                    # we generated nodes
                    # 因為只有作用在2個coordinate. 
                    skip_coordinate.append([previous_x,previous_y])

                    redo_travel=True

                    # current version is not stable!, redo will cuase strange curves.
                    # [BUT], if not use -1, some case will be lost if dot near the first dot.
                    resume_idx = -1
                    #resume_idx = idx
                    break
                    #redo_travel=True
                    #resume_idx = -1
                    #break

        if redo_travel:
            # check close path.
            self.reset_first_point(format_dict_array, spline_dict)


        return redo_travel, resume_idx, inside_stroke_dict,skip_coordinate
