import cv2
import numpy as np
import dlib
from math import hypot
import time
import os
import win32com.client as wincl

cap = cv2.VideoCapture(0)
board = np.zeros((300, 1500), np.uint8)
board[:] = 255

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("C:\\Users\\Gordei\\Desktop\\OxfordHack\\shape_predictor_68_face_landmarks.dat")

keyboard = np.zeros((600, 1000, 3), np.uint8)

# Bellow is the keyboard setup it's basically splits the entire keyboard in half so that you could iterate 
# through it in a timely maner

keys_set_1 = {0: "Q", 1: "W", 2: "E", 3: "R", 4: "T",
              5: "A", 6: "S", 7: "D", 8: "F", 9: "G",
              10: "Z", 11: "X", 12: "C", 13: "V", 14: "<"}
keys_set_2 = {0: "Y", 1: "U", 2: "I", 3: "O", 4: "P",
              5: "H", 6: "J", 7: "K", 8: "L", 9: "_",
              10: "V", 11: "B", 12: "N", 13: "M", 14: "<"}

def draw_letters(letter_index, text, letter_light):
    
    switcher = {
        0: [0,0],
        1: [200,0],
        2: [400,0],
        3: [600,0],
        4: [800,0],
        5: [0,200],
        6: [200,200],
        7: [400,200],
        8: [600,200],
        9: [800,200],
        10: [0,400],
        11: [200,400],
        12: [400,400],
        13: [600,400],
        14: [800,400]
    }

    x = switcher[letter_index][0]
    y = switcher[letter_index][1]

    width = 200
    height = 200
    th = 3 # thickness

    # Text settings
    font_letter = cv2.FONT_HERSHEY_PLAIN
    font_scale = 10
    thickness = 10
    text_size = cv2.getTextSize(text, font_letter, font_scale, thickness)[0]
    width_text, height_text = text_size[0], text_size[1]
    text_x = int((width - width_text) / 2) + x
    text_y = int((height + height_text) / 2) + y

    if letter_light is True:
        cv2.rectangle(keyboard, (x + th, y + th), (x + width - th, y + height - th), (255, 255, 255), -1)
        cv2.putText(keyboard, text, (text_x, text_y), font_letter, font_scale, (0, 0, 0), thickness)
    else:
        cv2.rectangle(keyboard, (x + th, y + th), (x + width - th, y + height - th), (100, 150, 255), -1)
        cv2.putText(keyboard, text, (text_x, text_y), font_letter, font_scale, (0, 0, 0), thickness)

def draw_menu():
    rows, cols, _ = keyboard.shape
    th_lines = 2
    cv2.line(keyboard, (int(cols/2) - int(th_lines/2), 0),(int(cols/2) - int(th_lines/2), rows),
             (0, 0, 0), th_lines)
    cv2.putText(keyboard, "LEFT", (80, 300), font, 6, (100, 150, 255), 10)
    cv2.putText(keyboard, "RIGHT", (80 + int(cols/2), 300), font, 6, (100, 150, 255), 10)

def midpoint(p1 ,p2):
    return int((p1.x + p2.x)/2), int((p1.y + p2.y)/2)

font = cv2.FONT_HERSHEY_PLAIN

def get_blinking_ratio(eye_points, facial_landmarks):
    left_point = (facial_landmarks.part(eye_points[0]).x, facial_landmarks.part(eye_points[0]).y)
    right_point = (facial_landmarks.part(eye_points[3]).x, facial_landmarks.part(eye_points[3]).y)
    center_top = midpoint(facial_landmarks.part(eye_points[1]), facial_landmarks.part(eye_points[2]))
    center_bottom = midpoint(facial_landmarks.part(eye_points[5]), facial_landmarks.part(eye_points[4]))

    hor_line = cv2.line(frame, left_point, right_point, (0, 255, 0), 2)
    ver_line = cv2.line(frame, center_top, center_bottom, (0, 255, 0), 2)

    hor_line_lenght = hypot((left_point[0] - right_point[0]), (left_point[1] - right_point[1]))
    ver_line_lenght = hypot((center_top[0] - center_bottom[0]), (center_top[1] - center_bottom[1]))

    ratio = hor_line_lenght / ver_line_lenght
    return ratio

def eyes_contour_points(facial_landmarks):
    left_eye = []
    right_eye = []
    for n in range(36, 42):
        x = facial_landmarks.part(n).x
        y = facial_landmarks.part(n).y
        left_eye.append([x, y])
    for n in range(42, 48):
        x = facial_landmarks.part(n).x
        y = facial_landmarks.part(n).y
        right_eye.append([x, y])
    left_eye = np.array(left_eye, np.int32)
    right_eye = np.array(right_eye, np.int32)
    return left_eye, right_eye

def get_gaze_ratio(eye_points, facial_landmarks):
    left_eye_region = np.array([(facial_landmarks.part(eye_points[0]).x, facial_landmarks.part(eye_points[0]).y),
                                (facial_landmarks.part(eye_points[1]).x, facial_landmarks.part(eye_points[1]).y),
                                (facial_landmarks.part(eye_points[2]).x, facial_landmarks.part(eye_points[2]).y),
                                (facial_landmarks.part(eye_points[3]).x, facial_landmarks.part(eye_points[3]).y),
                                (facial_landmarks.part(eye_points[4]).x, facial_landmarks.part(eye_points[4]).y),
                                (facial_landmarks.part(eye_points[5]).x, facial_landmarks.part(eye_points[5]).y)], np.int32)
    cv2.polylines(frame, [left_eye_region], True, (0, 0, 255), 2)

    height, width, _ = frame.shape
    mask = np.zeros((height, width), np.uint8)
    cv2.polylines(mask, [left_eye_region], True, 255, 1)
    cv2.fillPoly(mask, [left_eye_region], 255)
    eye = cv2.bitwise_and(gray, gray, mask=mask)

    min_x = np.min(left_eye_region[:, 0])
    max_x = np.max(left_eye_region[:, 0])
    min_y = np.min(left_eye_region[:, 1])
    max_y = np.max(left_eye_region[:, 1])

    gray_eye = eye[min_y: max_y, min_x: max_x]
    _, threshold_eye = cv2.threshold(gray_eye, 70, 255, cv2.THRESH_BINARY)
    height, width = threshold_eye.shape
    left_side_threshold = threshold_eye[0: height, 0: int(width / 2)]
    left_side_white = cv2.countNonZero(left_side_threshold)

    right_side_threshold = threshold_eye[0: height, int(width / 2): width]
    right_side_white = cv2.countNonZero(right_side_threshold)

    if left_side_white == 0:
        gaze_ratio = 1
    elif right_side_white == 0:
        gaze_ratio = 5
    else:
        gaze_ratio = left_side_white / right_side_white
    return gaze_ratio

# Counters
frames = 0
letter_index = 0
blinking_frames = 0
blink_frames = 6
frames_active_letter = 9

# Text and keyboard settings
text = ""
keyboard_selected = "right"
last_keyboard_selected = "right"
select_keyboard_menu = False
keyboard_selection_frames = 0

while True:
    _, frame = cap.read()
    frame = cv2.resize(frame, None, fx=0.8, fy=0.8)
    rows, cols, _ = frame.shape
    keyboard[:] = (0, 0, 0)
    frames += 1
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Draw a white space for loading bar
    frame[rows - 50: rows, 0: cols] = (255, 255, 255)

    if select_keyboard_menu is True:
        draw_menu()

    # Keyboard selected
    if keyboard_selected == "left":
        keys_set = keys_set_1
    else:
        keys_set = keys_set_2
    
    active_letter = keys_set[letter_index]

    # Face detection
    faces = detector(gray)
    for face in faces:
        landmarks = predictor(gray, face)

        left_eye, right_eye = eyes_contour_points(landmarks)

        # Detect blinking
        left_eye_ratio = get_blinking_ratio([36, 37, 38, 39, 40, 41], landmarks)
        right_eye_ratio = get_blinking_ratio([42, 43, 44, 45, 46, 47], landmarks)
        blinking_ratio = (left_eye_ratio + right_eye_ratio) / 2

        # Eyes color
        cv2.polylines(frame, [left_eye], True, (0, 0, 255), 2)
        cv2.polylines(frame, [right_eye], True, (0, 0, 255), 2)


        if select_keyboard_menu is True:
            
            # Detecting gaze to select Left or Right keybaord
            gaze_ratio_left_eye = get_gaze_ratio([36, 37, 38, 39, 40, 41], landmarks)
            gaze_ratio_right_eye = get_gaze_ratio([42, 43, 44, 45, 46, 47], landmarks)
            gaze_ratio = (gaze_ratio_right_eye + gaze_ratio_left_eye) / 2

            if gaze_ratio <= 0.9: #XXXXXXXXXXXXXXXXXXXXXX
                keyboard_selected = "right"
                keyboard_selection_frames += 1

                if keyboard_selection_frames == 3:
                    select_keyboard_menu = False
                    # Set frames count to 0 when keyboard selected
                    frames = 0
                    keyboard_selection_frames = 0
                if keyboard_selected != last_keyboard_selected:
                    last_keyboard_selected = keyboard_selected
                    keyboard_selection_frames = 0
                    
            else:
                keyboard_selected = "left"
                keyboard_selection_frames += 1
                if keyboard_selection_frames == 7:
                    select_keyboard_menu = False
                    # Set frames count to 0 when keyboard selected
                    frames = 0
                if keyboard_selected != last_keyboard_selected:
                    last_keyboard_selected = keyboard_selected
                    keyboard_selection_frames = 0

        else:
            # Detect the blinking to select the key that is lighting up
            if blinking_ratio > 5:
                blinking_frames += 1
                frames -= 1

                # Show green eyes when closed
                #cv2.polylines(frame, [left_eye], True, (0, 255, 0), 2)
                #cv2.polylines(frame, [right_eye], True, (0, 255, 0), 2)

                # Typing letter
                if blinking_frames == blink_frames:
                    if active_letter != "<" and active_letter != "_":
                        text += active_letter
                    if active_letter == "_":
                        text += " "
                    select_keyboard_menu = True
                    time.sleep(.5)

            else:
                blinking_frames = 0


    # Display letters on the keyboard
    if select_keyboard_menu is False:
        if frames == frames_active_letter:
            letter_index += 1
            letter_index %= 15
            frames = 0
        for i in range(15):
            if i == letter_index:
                light = True
            else:
                light = False
            draw_letters(i, keys_set[i], light)

    # Show the text we're writing on the board
    cv2.putText(board, text, (80, 100), font, 9, 0, 10)
    
    # Blinking loading bar
    percentage_blinking = blinking_frames / blink_frames
    loading_x = int(cols * percentage_blinking)
    cv2.rectangle(frame, (0, rows - 50), (loading_x, rows), (100, 150, 255), -1)


    #cv2.imshow("Camera", frame)
    cv2.imshow("Keyboard", keyboard)
    cv2.imshow("Text", board)

    key = cv2.waitKey(1)
    if key == 27:
        break

save_path = "C:\\Users\\Gordei\\Desktop\\OxfordHack"
completeName = os.path.join(save_path, "output.txt")         
file1 = open(completeName, "w")
file1.write(text)
file1.close()

speak = wincl.Dispatch("SAPI.SpVoice")
speak.Speak(text)

cap.release()
cv2.destroyAllWindows()