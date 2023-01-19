print("iniciando código, aguarde 1min03seg, aproximadamente")

import face_recognition
import cv2
import numpy as np
import os
import smtplib
import imghdr
import RPi.GPIO as GPIO     # Importa biblioteca GPIO PIN
import time                 # Para função DELAY

GPIO.setmode(GPIO.BOARD)    # Habilitar toda placa raspberry-pi
GPIO.setwarnings(False)     # Aviso para evitar usar o mesmo PINO
buzzer_pin =36
motor_pin1 =31
motor_pin2 =32
LED_PIN = 29
switch_pin =4
pir_pin = 18
GPIO.setup(LED_PIN,GPIO.OUT)   # Set o pino como saída
GPIO.setup(motor_pin1, GPIO.OUT) 
GPIO.setup(motor_pin2, GPIO.OUT) 
GPIO.setup(buzzer_pin,GPIO.OUT)   # Set o pino como saída
GPIO.setup(switch_pin,GPIO.IN,pull_up_down=GPIO.PUD_UP)   # Set o pino como entrada
GPIO.setup(pir_pin,GPIO.IN)


CurrentFolder = os.getcwd() #Ler o diretório onde ficará as imagens
image = "/home/alisson/Documentos/Trabalho Final/alisson1.png"
image2 = "/home/alisson/Documentos/Trabalho Final/alisson7.png"
image3 = "/home/alisson/Documentos/Trabalho Final/gilberto.png"

# Referencia o dispositivo webcam #0
video_capture = cv2.VideoCapture(0)

# Carrega a primeira imagem de amostra e para reconhecê-la.
alisson1_image = face_recognition.load_image_file(image)
alisson1_face_encoding = face_recognition.face_encodings(alisson1_image)[0]

# Carrega a segunda imagem de amostra e para reconhecê-la.
alisson7_image = face_recognition.load_image_file(image2)
alisson7_face_encoding = face_recognition.face_encodings(alisson7_image)[0]

# Carrega a terceira imagem de amostra e para reconhecê-la.
gilberto_image = face_recognition.load_image_file(image3)
gilberto_face_encoding = face_recognition.face_encodings(gilberto_image)[0]

# Cria arrays de codificações de face conhecidas e seus nomes
known_face_encodings = [
    alisson1_face_encoding,
    alisson7_face_encoding,
    gilberto_face_encoding
]
known_face_names = [
    "alisson1",
    "alisson7",
    "gilberto"
]

#variável para armazenar o status da pessoa na webcam
inside_home = 0
door_open_status =0
# Inicializar algumas variáveis
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True


# Constantes de tempo
E_PULSE = 0.0005
E_DELAY = 0.0005
delay = 1

# Definir atraso entre as leituras
delay = 5

GPIO.output(LED_PIN,GPIO.LOW)  #LED OFF
GPIO.output(buzzer_pin,GPIO.LOW)  #buzzer OFF
GPIO.output(motor_pin1,GPIO.LOW)  #motor OFF
GPIO.output(motor_pin2,GPIO.LOW)  #motor OFF  
while True:
    #Entrada da switch
    door_open_status = 0
    
    if GPIO.input(switch_pin) == GPIO.HIGH:
        GPIO.output(LED_PIN,GPIO.HIGH)  #LED ON
        GPIO.output(buzzer_pin,GPIO.HIGH)  #LED ON
        time.sleep(2)
        GPIO.output(LED_PIN,GPIO.LOW)  #LED ON
        GPIO.output(buzzer_pin,GPIO.LOW)  #buzzer OFF
        while(1):
            if GPIO.input(pir_pin) == GPIO.HIGH:
                 #idetificando alguém
                 print("pessoa não autorizada")
                 inside_home = 1                
            else :
                 #idetificando alguém
                 print("pessoa na entrada autorizada")
                 inside_home = 0         
            # Grab a single frame of video
            ret, frame = video_capture.read()

            # Resize frame of video to 1/4 size for faster face recognition processing
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

            # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
            rgb_small_frame = small_frame[:, :, ::-1]

            # Only process every other frame of video to save time
            if process_this_frame:
                # Find all the faces and face encodings in the current frame of video
                face_locations = face_recognition.face_locations(rgb_small_frame)
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
                
                face_names = []
                for face_encoding in face_encodings:
                    # See if the face is a match for the known face(s)
                    matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                    name = "Unknown"

                    # # If a match was found in known_face_encodings, just use the first one.
                    # if True in matches:
                    #     first_match_index = matches.index(True)
                    #     name = known_face_names[first_match_index]

                    # Or instead, use the known face with the smallest distance to the new face
                    face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        name = known_face_names[best_match_index]
                    face_names.append(name)
                    if(name == "Unknown"):
                        
                        if(inside_home == 0):
                            GPIO.output(LED_PIN,GPIO.HIGH)
                            i = 0
                            while i < 10:
                                print("pessoa não autorizada")
                                #return_value, image = video_capture.read()
                                cv2.imwrite('opencv.png', frame)
                                i += 1
                                
                                with open('opencv.png', 'rb') as f:
                                    image_data = f.read()
                                    image_type = imghdr.what(f.name)
                                    image_name = f.name
                                
                    else:
                        GPIO.output(LED_PIN,GPIO.LOW)  #LED OFF
                        if(door_open_status == 0):
                            door_open_status = 1
                            GPIO.output(motor_pin1,GPIO.LOW)  #motor OFF
                            GPIO.output(motor_pin2,GPIO.HIGH)  #motor ON
                            time.sleep(0.3)
                            GPIO.output(motor_pin1,GPIO.LOW)  #motor OFF
                            GPIO.output(motor_pin2,GPIO.LOW)  #motor OFF
                            time.sleep(2)
                            GPIO.output(motor_pin1,GPIO.HIGH)  #motor ON
                            GPIO.output(motor_pin2,GPIO.LOW)  #motor OFF
                            time.sleep(0.3)
                            GPIO.output(motor_pin1,GPIO.LOW)  #motor OFF
                            GPIO.output(motor_pin2,GPIO.LOW)  #motor OFF                        
                            time.sleep(1)
                                    
            process_this_frame = not process_this_frame

            # Abre a janela com a imagem da webcam
            for (top, right, bottom, left), name in zip(face_locations, face_names):
                # Scale back up face locations since the frame we detected in was scaled to 1/4 size
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                # Draw a box around the face
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

                # Mostrar o nome abaixo do rosto
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
                print("pessoa autorizada")
                GPIO.output(LED_PIN,GPIO.HIGH)  #LED ON
                time.sleep(2)
                GPIO.output(LED_PIN,GPIO.LOW)   #LED OFF 
                
            # Display the resulting image
            cv2.imshow('Video', frame)
            if (cv2.waitKey(2) == 27):
                cv2.destroyAllWindows()
                break


# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()
