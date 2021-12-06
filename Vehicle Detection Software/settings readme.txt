Settings readme.
Welcome to settings.
The openCV ui options are not very accomodating so it may require further
explanation.

You should see:
	One settings pannel with six sliders;
	A delta window;
	A threshold window; and
	A tracking window.

The tracking window displays the original video frame with moving cars
highlighed with a green rectangle.

The Delta window shows a black and white frame. The frame is black and moving
objects are drawn in white.

The Threshold window is similar to the delta window, but it only displays the
strongest movement (the brightest areas of delta).

The settings window allows you to adjust variables which effects what is shown
in the other windows.

Blur
This is the ammount of gaussian blur applied to the frame. This eliminates
video grain and reduces detail which might cause false positives.
If there are too many non car elements being drawn on the delta frame,
try increasing this value.
If cars are bleeding into each other too much decrease this value.

Buffer
This is the frame buffer. Movement is detected by comparing the current frame
to the previous frame. You can see this in the delta window.
If you cannot see the cars well in the delta window increase this value.
Be aware that it will increase amplify all movement includeing movement you
might not want to track.
At higher values objects may squash and stretch as they change speed.

Threshold
Threshold eliminates faint movement from the delta frame.
If there are too many non car elements apearing on the thresh frame, but delta
frame shows cars clearly, decrease this value.
If the cars are clear on the delta frame, but not visible on the thresh frame,
decrease this value.

Fill
This fills in gaps between nearby shapes.
If the cars in your threshold window are too fragmented increase this value.
This will also fill gaps between shapes that are not cars.

Min Area
This is the minimum area of detected contours that we should consider a car.
If cars are identified well in the threshold window but not highlighted in the
tracking window decrease Min Area.
If small artifacts you don't want to track are being highlighted in the
tracking window, increase Min Area.

OK
It seems like the button function of OpenCV for python is not implemented.
When you are done change the OK value to 1.