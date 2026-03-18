import cv2
import numpy as np
import mediapipe as mp

# Initialize MediaPipe Hands module
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# Initialize webcam
cap = cv2.VideoCapture(0)

# Drawing variables
canvas = None
prev_x, prev_y = 0, 0
draw_color = (255, 0, 0)  # Default color: Blue
brush_thickness = 10
eraser_thickness = 50
eraser_mode = False

# Define color buttons and sizes
button_height = 80
button_width = 80
color_palette = {
    'blue': ((20, 20), (20 + button_width, 20 + button_height), (255, 0, 0)),
    'green': ((120, 20), (120 + button_width, 20 + button_height), (0, 255, 0)),
    'red': ((220, 20), (220 + button_width, 20 + button_height), (0, 0, 255)),
    'yellow': ((320, 20), (320 + button_width, 20 + button_height), (0, 255, 255)),
    'eraser': ((420, 20), (420 + button_width, 20 + button_height), (0, 0, 0)),
    'stop': ((520, 20), (520 + button_width, 20 + button_height), (0, 0, 139))  # Dark red for stop button
}

# Keep track of active tool
active_tool = 'blue'  # default color name

def draw_buttons(img, active_tool_name):
    """Draw color and eraser buttons on screen, highlight the active one."""
    for name, ((x1, y1), (x2, y2), color) in color_palette.items():
        # Draw filled color boxes
        cv2.rectangle(img, (x1, y1), (x2, y2), color, cv2.FILLED)

        # Add text label
        text_color = (255, 255, 255) if name != 'yellow' else (0, 0, 0)
        cv2.putText(img, name, (x1 + 5, y2 + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, text_color, 2)

        # Highlight the active tool
        if name == active_tool_name:
            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 255, 255), 3)

# Setup MediaPipe Hands
with mp_hands.Hands(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
        max_num_hands=1) as hands:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, _ = frame.shape

        # Create canvas if not already done
        if canvas is None:
            canvas = np.zeros_like(frame)

        # Draw color palette with active highlight
        draw_buttons(frame, active_tool)

        # Process hand landmarks
        result = hands.process(frame_rgb)

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                lm_list = []
                for id, lm in enumerate(hand_landmarks.landmark):
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lm_list.append((cx, cy))

                if lm_list:
                    index_finger = lm_list[8]
                    middle_finger = lm_list[12]

                    # Gesture Detection - Improved finger distance calculation
                    fingers_up = abs(index_finger[1] - middle_finger[1]) < 60

                    # SELECTION MODE (2 Fingers Up) -> Change color/tool
                    if fingers_up:
                        prev_x, prev_y = 0, 0
                        x, y = index_finger

                        for name, ((x1, y1), (x2, y2), color) in color_palette.items():
                            if x1 < x < x2 and y1 < y < y2:
                                active_tool = name  # Update active tool highlight

                                if name == 'eraser':
                                    eraser_mode = True
                                elif name == 'stop':
                                    # Exit the application when stop button is pressed
                                    cv2.destroyAllWindows()
                                    cap.release()
                                    exit()
                                else:
                                    eraser_mode = False
                                    draw_color = color

                                # Draw highlight on selected button (already handled in draw_buttons)
                                break  # Exit loop once matched

                    # DRAWING MODE (Index Finger Only)
                    else:
                        # Only draw if NOT in selection mode (one finger up)
                        x, y = index_finger

                        if prev_x == 0 and prev_y == 0:
                            prev_x, prev_y = x, y

                        if eraser_mode:
                            cv2.line(canvas, (prev_x, prev_y), (x, y), (0, 0, 0), eraser_thickness)
                        else:
                            cv2.line(canvas, (prev_x, prev_y), (x, y), draw_color, brush_thickness)

                        prev_x, prev_y = x, y
        else:
            prev_x, prev_y = 0, 0

        # Merge canvas with the frame
        gray_canvas = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray_canvas, 20, 255, cv2.THRESH_BINARY)
        inv_mask = cv2.bitwise_not(mask)

        frame_bg = cv2.bitwise_and(frame, frame, mask=inv_mask)
        canvas_fg = cv2.bitwise_and(canvas, canvas, mask=mask)

        combined_frame = cv2.add(frame_bg, canvas_fg)

        # Display Brush Info - Enhanced with better visibility
        cv2.putText(combined_frame, f'Brush: {brush_thickness}', (10, h - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Add brush size control instructions
        cv2.putText(combined_frame, "'+' Increase size", (w - 200, h - 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(combined_frame, "'-' Decrease size", (w - 200, h - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        # Show window
        cv2.imshow("Air Canvas - Drawing App", combined_frame)

        # Keyboard Controls
        key = cv2.waitKey(1) & 0xFF

        # Quit
        if key == ord('q'):
            break

        # Clear canvas
        if key == ord('c'):
            canvas = np.zeros_like(frame)

        # Save canvas
        if key == ord('s'):
            cv2.imwrite('my_air_canvas_drawing.png', canvas)
            print("Drawing saved as 'my_air_canvas_drawing.png'")

        # Increase brush thickness
        if key == ord('+') or key == ord('='):
            brush_thickness += 5
            print(f"Brush thickness increased: {brush_thickness}")

        # Decrease brush thickness
        if key == ord('-') or key == ord('_'):
            brush_thickness = max(5, brush_thickness - 5)
            print(f"Brush thickness decreased: {brush_thickness}")

# Release resources
cap.release()
cv2.destroyAllWindows()
