import cv2 as cv
import numpy as np

img = cv.imread("task5.png", 1)
img_balls = cv.imread("task5.png", 0)
img_balls_res = cv.imread("task5.png", 1)
img_stick = cv.imread("task5.png", 0)
img_stick_res = cv.imread("task5.png", 1)
cv.inRange(img, (255, 255, 255), (255, 255, 255), img_balls) #Extracting balls
cv.inRange(img, (0, 0, 220), (0, 0, 255), img_stick) #Extracting stick

img_stick_1 = img_stick
cv.medianBlur(img_stick, 3, img_stick) # To remove noise
cv.namedWindow("STICK", cv.WINDOW_NORMAL)
cv.imshow("STICK", img_stick)

cv.namedWindow("INPUT IMAGE", cv.WINDOW_NORMAL)
cv.namedWindow("ONLY BALLS", cv.WINDOW_NORMAL)
cv.imshow("INPUT IMAGE", img)
cv.imshow("ONLY BALLS", img_balls)




lines = cv.HoughLines(img_stick, 1,np.pi/180, 10) # Detecing stick

theta1 = 0
r1 = 0

#Finding the average r and theta for best possible line
for t in lines:
    for r, theta in t:
        theta1 = theta1 + theta
        r1 = r1 + r

theta1 = theta1/len(lines)
r1 = r1/len(lines)

#print(stick_end_points)

a = np.cos(theta1)
b = np.sin(theta1)
x1 = int((r1 * a + 1000 * (-b) + 0.5))
y1 = int(r1 * b + 1000 * (a) + 0.5)
x2 = int((r1 * a - 1000 * (-b) + 0.5))
y2 = int(r1 * b - 1000 * (a) + 0.5)

#Finding noisless stick points
temp = np.zeros((img.shape[0], img.shape[1], 1))
cv.line(temp, (x1, y1), (x2, y2), (255), 1)
temp_stick_points = []
stick_points = []
temp_list = []
for i in range(0, temp.shape[0]):
    for j in range(0, temp.shape[1]):
        if(temp[i, j] == 255):
            if(img_stick_1[i, j] == 255):
                temp_list.append([j, i])
            else:
                if(len(temp_list)!=0):
                    temp_stick_points.append(temp_list)

temp_counter = -1
max_len = 0
max_len_index = 0
for points in temp_stick_points:
    temp_counter = temp_counter + 1
    if(len(points) > max_len):
        max_len = len(points)
        max_len_index = temp_counter

stick_points = temp_stick_points[max_len_index]

#Finding stick end points
stick_end_points = []
stick_end_points.append(stick_points[0])
stick_end_points.append(stick_points[len(stick_points) - 1])
print(stick_end_points)

#Finding angle of velocity
angle_of_velocity = np.arctan((y1 - y2)/(x2 - x1))
if(angle_of_velocity < 0):
    angle_of_velocity = np.pi + angle_of_velocity
print(angle_of_velocity*180/np.pi)


velocity = input("Enter the velocity: ")
no_of_collisions = input("Enter the number of collisions: ")
no_of_collisions = int(no_of_collisions)
print(str(velocity) + " pixel/second")
velocity = float(velocity)

#print(lines)
#print(180*((lines.item(1, 0, 1) - lines.item(0, 0, 1))/(lines.item(1, 0, 0) - lines.item(0, 0, 0)))/np.pi)

cv.medianBlur(img_balls, 5, img_balls)
circles = cv.HoughCircles(img_balls,cv.HOUGH_GRADIENT,2,4,param1=20,param2=55,minRadius=0,maxRadius=0) #Detecing balls

balls_at_rest = []
for i in circles[0,:]:
    balls_at_rest.append(list(i))
    # draw the outer circle
    #cv.circle(img_balls_res,(i[0],i[1]),i[2],(0,255,0),2)
    # draw the center of the circle
    #cv.circle(img_balls_res,(i[0],i[1]),2,(0,0,255),3)

#Finding first ball and head of stick
min_dist = img_stick.shape[0]*img_stick.shape[1]
first_ball = []
stick_head = []
for i in stick_end_points:
    for j in circles[0, :]:
        dist = np.sqrt(np.square(i[0] - j[0]) + np.square(i[1] - j[1]))
        if(dist < min_dist):
            min_dist = dist
            stick_head = i
            first_ball = j

moving_balls = []
moving_balls.append(first_ball)

if(not((first_ball[0] >= stick_head[0] and first_ball[1] <= stick_head[1]) or (first_ball[0] <= stick_head[0] and first_ball[1] <= stick_head[1]))):
    velocity = velocity * -1

for i in balls_at_rest:
    if(i[0] == moving_balls[0][0] and i[1] == moving_balls[0][1] and i[2] == moving_balls[0][2]):
        balls_at_rest.remove(i)

sign_x = 1
sign_y = -1

velocity_x = velocity * np.cos(angle_of_velocity)
velocity_y = velocity * np.sin(angle_of_velocity)

collision_points = []

#Main animation starts here
while(no_of_collisions):
    animation = np.zeros((img.shape[0], img.shape[1], 3))
    for i in collision_points:			#Drawing points of collisions
        cv.circle(animation, tuple(i), 1, (0, 0, 255), 5)

    #Finding ball to ball collision
    index_moving = 0
    for ball_motion in moving_balls:
        index_rest = 0
        for ball_rest in balls_at_rest:
            dist = np.sqrt(np.square(ball_rest[0] - ball_motion[0]) + np.square(ball_rest[1] - ball_motion[1]))
            if(dist <= ball_rest[2] + ball_motion[2]):
                #moving_balls.remove(ball_motion)
                del moving_balls[index_moving]
                del balls_at_rest[index_rest]
                moving_balls.append(ball_rest)
                #remove_element(moving_balls, ball_motion)
                #remove_element(balls_at_rest, ball_rest)
                #balls_at_rest.remove(ball_rest)
                balls_at_rest.append(list(ball_motion))
                collision_points.append([int((ball_rest[0] + ball_motion[0])/2), int((ball_rest[1] + ball_motion[1])/2)])
                print("Collision a point: " + str((ball_rest[0] + ball_motion[0])/2) + ", " + str((ball_rest[1] + ball_motion[1])/2))
                no_of_collisions = no_of_collisions - 1
                break
            index_rest = index_rest + 1
        index_moving = index_moving + 1
    #Finding ball to wall collisions
    for ball_motion in moving_balls:
        if(ball_motion[0] <= ball_motion[2] or animation.shape[1] - ball_motion[0] <= ball_motion[2]):
            no_of_collisions = no_of_collisions - 1
            if(ball_motion[0] <= ball_motion[2]):
                collision_points.append([int(0), int(ball_motion[1])])
                print("Collision with vertical ball at point " + str([0, ball_motion[1]]))
            else:
                collision_points.append([int(animation.shape[1] - 1), int(ball_motion[1])])
                print("Collision with vertical ball at point " + str([animation.shape[1] - 1, ball_motion[1]]))
            velocity_x = velocity_x * -1
        elif(ball_motion[1] <= ball_motion[2] or animation.shape[0] - ball_motion[1] <= ball_motion[2]):
            no_of_collisions = no_of_collisions - 1
            if (ball_motion[1] <= ball_motion[2]):
                collision_points.append([int(ball_motion[0]), int(0)])
                print("Collision with horizontal ball at point " + str([ball_motion[0], 0]))
            else:
                collision_points.append([int(ball_motion[0]), int(animation.shape[0] - 1)])
                print("Collision with horizontal ball at point " + str([int(ball_motion[0]), int(animation.shape[0] - 1)]))
            velocity_y = velocity_y * -1

    #Drawing all the balls
    for ball in moving_balls:
        cv.circle(animation, (int(ball[0]), int(ball[1])), int(ball[2]), (255, 0, 0), -1)
        ball[0] = ball[0] + velocity_x
        ball[1] = ball[1] - velocity_y
    for ball in balls_at_rest:
        cv.circle(animation, (int(ball[0]), int(ball[1])), int(ball[2]), (255, 255, 255), -1)

    cv.namedWindow("Animation", cv.WINDOW_NORMAL)
    cv.imshow("Animation", animation)
    cv.waitKey(10)

cv.waitKey(0)
cv.destroyAllWindows()
