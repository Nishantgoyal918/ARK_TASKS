import cv2 as cv
import numpy as np
import random

#For object tracking using centroid tracking algorithm
class Object_Tracker:
    #Adding new object to list
    def add_object(self, faces):
        for (x, y, w, h) in faces:
            self.objects_list.append([x, y, w, h])
    #Updating the position of object in list
    def update_object(self, faces):
        min_dist = 10000000
        object_index = -1
        min_index = 0
        for objects in self.objects_list:
            object_index = object_index + 1
            index = -1
            if (len(faces) != 0):
                for (x, y, w, h) in faces:
                    index = index + 1
                    dist = np.sqrt(np.square((objects[0] + objects[2] / 2) - (x + w / 2)) + np.square(
                        (objects[1] + objects[3] / 2) - (y + h / 2)))
                    if dist < min_dist:
                        min_dist = dist
                        min_index = index

                self.objects_list[object_index] = list(faces[min_index])
    #Drawing a rectangular frame around the object
    def draw_tracker(self, img):
        for objects in self.objects_list:
            cv.rectangle(img, (objects[0], objects[1]), (objects[0] + objects[2], objects[1] + objects[3]), (0, 255, 0), 3)
            cv.circle(img, (int(objects[0] + objects[2]/2), int(objects[1] + objects[3]/2)), 1, (0, 0, 255), 3)
#Main game class
class Game(Object_Tracker):
    def __init__(self, window_shape):
        self.objects_list = []
        self.window_shape = window_shape
        self.obstacles_list = []
        self.obstacle_width = 60
        self.score = 0
        start_x = 180
        for i in range(0, int(window_shape[1]/60)):   #Creating a list of random obstacles
            length = random.randint(int(window_shape[0]/4), int(window_shape[0]*3/4))
            self.obstacles_list.append([length, start_x, random.randint(0, 1), 0]) #obstacles_list contain lenght, stating x coord, position up or down, whether it is out of screen now or not
            start_x = start_x + 120
        print(self.obstacles_list)

    def draw_flappy_bird(self, img):
        for objects in self.objects_list:
            center_x = int(objects[0] + objects[2]/2)
            center_y = int(objects[1] + objects[3]/2)
            if(center_x<15 and center_y<15):
                cv.rectangle(img, (0, 0), (center_x + 15, center_y + 15), (0, 136, 255), -1)
            elif(center_x<15):
                cv.rectangle(img, (0, center_y - 15), (center_x + 15, center_y + 15), (0, 136, 255), -1)
            elif(center_y<15):
                cv.rectangle(img, (center_x - 15, 0), (center_x + 15, center_y + 15), (0, 136, 255), -1)
            else:
                cv.rectangle(img, (center_x - 15, center_y - 15), (center_x + 15, center_y + 15), (0, 136, 255), -1)

    def draw_obstacle(self, game_screen):
        for obstacles in self.obstacles_list:
            if(obstacles[1] < game_screen.shape[1]):
                temp = obstacles[2]
                if(obstacles[1] < 0):
                    if(temp == 0):
                        cv.rectangle(game_screen, (0, 0), (obstacles[1] + self.obstacle_width, obstacles[0]), (33, 120, 4), -1)
                    else:
                        cv.rectangle(game_screen, (0, game_screen.shape[0] - obstacles[0]), (obstacles[1] + self.obstacle_width, game_screen.shape[0]), (33, 120, 4), -1)
                else:
                    if (temp == 0):
                        cv.rectangle(game_screen, (obstacles[1], 0), (obstacles[1] + self.obstacle_width, obstacles[0]), (33, 120, 4), -1)
                    else:
                        cv.rectangle(game_screen, (obstacles[1], game_screen.shape[0] - obstacles[0]), (obstacles[1] + self.obstacle_width, game_screen.shape[0]), (33, 120, 4), -1)
            if(obstacles[1] + self.obstacle_width < 0):
                obstacles[3] = 1

    def start_game(self, game_screen, webcam): #This will be called unless the game started
        cv.circle(game_screen, (100, int(game_screen.shape[0]/2)), 50, (0, 255, 0), 3)
        cv.putText(game_screen, "START", (70, int(game_screen.shape[0]/2) + 10), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2);
        self.draw_tracker(webcam)
        self.draw_obstacle(game_screen)
        self.draw_flappy_bird(game_screen)
        cv.putText(game_screen, str(self.score), (game_screen.shape[1] - 50, 30), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2);
        cx = self.objects_list[0][0] + self.objects_list[0][2]/2
        cy = self.objects_list[0][1] + self.objects_list[0][3]/2

        if(np.sqrt(np.square(cx - 100) + np.square(cy - int(game_screen.shape[0]/2))) <= 50):
            print("GAME STARTED")
            return 1

        return 0

    def obstacles_list_update(self):
        index = -1
        for obstacles in self.obstacles_list:
            index = index + 1
            if(obstacles[3] == 1):
                self.obstacles_list.pop(index)
                length = random.randint(int(self.window_shape[0] / 4), int(self.window_shape[0] * 3 / 4))
                self.obstacles_list.append([length, self.obstacles_list[len(self.obstacles_list) - 1][1] + 120, random.randint(0, 1), 0])

    def check_game_status(self, game_screen):
        cx = self.objects_list[0][0] + self.objects_list[0][2] / 2
        cx = int(cx)
        cy = self.objects_list[0][1] + self.objects_list[0][3] / 2
        cy = int(cy)
        game_over = 0
        if (cx + 15 >= 0 and cx + 15 < self.window_shape[1] and cy + 15 >= 0 and cy + 15 < self.window_shape[0]):
            for obstacles in self.obstacles_list:
                if(obstacles[1] > cx+16+60):
                    break
                obs_x = obstacles[1]
                obs_h = obstacles[0]

                if(obstacles[2] == 0):
                    if(cx>=obs_x-14 and cx<=obs_x+14 and cy<=obs_h + 14):
                        game_over = 1
                else:
                    if (cx >= obs_x - 14 and cx <= obs_x + 14 and cy >= (self.window_shape[0] - (obs_h + 14))):
                        game_over = 1
        else:
            game_over = 1

        if(game_over == 1):
            cv.putText(game_screen, "GAME OVER", (int(game_screen.shape[1]/2) - 110, int(game_screen.shape[0]/2) - 20), cv.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 4)
            print("YOUR SCORE = " + str(self.score))
            return 0
        return 1

    def continue_game(self, game_screen, webcam):
        self.draw_tracker(webcam)
        self.draw_obstacle(game_screen)
        self.draw_flappy_bird(game_screen)
        game_status = self.check_game_status(game_screen)
        cv.putText(game_screen, str(self.score), (game_screen.shape[1] - 50, 30), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2);
        for obstacles in self.obstacles_list:
            obstacles[1] = obstacles[1] - 2
        self.obstacles_list_update()
        self.score = self.score + 1
        return game_status

face_cascade = cv.CascadeClassifier('haarcascade_frontalface_default.xml')
counter = 0;

cap = cv.VideoCapture(0)
fourcc = cv.VideoWriter_fourcc(*'XVID')
out = cv.VideoWriter('output.avi',fourcc, 20.0, (640,480))
g1 = Game(cap.read()[1].shape)
game_started = 0
game_status = 1
if(not(cap.isOpened())):
    print("Error Opening the camera!")
else:
    while(True):
        ret, webcam = cap.read()
        gray = cv.cvtColor(webcam, cv.COLOR_BGR2GRAY)
        ret, game_screen = cap.read()

        faces = face_cascade.detectMultiScale(gray, 1.1, 5)
        if (len(faces) != 0):
            counter = counter + 1

        if (counter == 1):
            g1.add_object(faces)
        else:
            g1.update_object(faces)

        if(game_started == 0 and counter>=1):
            game_started = g1.start_game(game_screen, webcam)
        elif(game_started!=0 and counter>=1):
            game_status = g1.continue_game(game_screen, webcam)
	
        cv.namedWindow("WEBCAM")
        cv.imshow("WEBCAM", webcam)
        cv.namedWindow("GAME_SCREEN")
        out.write(game_screen)
        cv.imshow("GAME_SCREEN", game_screen)
        if(game_status == 1):
            cv.waitKey(1)
        else:
            cv.waitKey(5000)
            break
