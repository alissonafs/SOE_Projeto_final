#include <opencv2/opencv.hpp>
#include <iostream>
#include <string>
#include <cstring>
#include <stdio.h>
#include <time.h>
#include <string.h>
#include <stdlib.h>
#include <mutex>
#include <fstream>


using namespace cv;
using namespace std;

bool stop_capture = false;

char str1[150];
char *nomeData()
{
   time_t mytime;
   mytime = time(NULL);
   struct tm tm = *localtime(&mytime);
   char str2[50];
   char *str3 = (char*)malloc(50);
   sprintf(str2,"%d", tm.tm_mday);
   strcpy(str3,"_"); strcat(str3,str2);
   strcat(str3,"_"); sprintf(str2,"%d",tm.tm_mon+1); strcat(str3,str2);
   strcat(str3,"_");  sprintf(str2,"%d",tm.tm_year+1900); strcat(str3,str2);
   strcat(str3,"__");  sprintf(str2,"%d",tm.tm_hour); strcat(str3,str2);
   strcat(str3,"_");  sprintf(str2,"%d",tm.tm_min+2); strcat(str3,str2);
   return(str3);
}

std::mutex logMutex;

bool fileExists(std::string& fileName) {
    return static_cast<bool>(std::ifstream(fileName));
}

template <typename filename, typename T1, typename T2, typename T3, typename T4>
bool addArqCSV(filename &fileName, T1 coluna1, T2 coluna2, T3 coluna3, T4 coluna4) {
    std::lock_guard<std::mutex> csvLock(logMutex);
    std::fstream file;
    file.open (fileName, std::ios::out | std::ios::app);
    if (file) {
        file << "\"" << coluna1 << "\",";
        file << "\"" << coluna2 << "\",";
        file << "\"" << coluna3 << "\",";
        file << "\"" << coluna4 << "\"";
        file <<  std::endl;
        return true;
    } else {
        return false;
    }
}


int main(int argc, char** argv)
{
  // +++++++++++++++++        
    chat varNome[150];
  // +++++++++++++++++        
// Load the two images
Mat image1 = imread("/home/alisson/Documentos/Trabalho_Final/alisson1.jpg");
Mat image2 = imread("/home/alisson/Documentos/Trabalho_Final/gilberto.jpg");

// Check if the images were loaded successfully
if (!image1.data || !image2.data)
{
    cout << "Não foi possível carregar as imagens" << endl;
    return 1;
}

// Open the camera stream
VideoCapture cap(0);

// Check if the camera was opened successfully
if (!cap.isOpened())
{
    cout << "Não foi possível abrir a câmera" << endl;
    return 1;
}

// Resize the images
Size new_size(800, 600);
resize(image1, image1, new_size);
resize(image2, image2, new_size);

// Convert the images to grayscale
cvtColor(image1, image1, COLOR_BGR2GRAY);
cvtColor(image2, image2, COLOR_BGR2GRAY);

while (!stop_capture)
{
    // Capture a single frame from the camera
    Mat camera_image;
    cap >> camera_image;

    // Resize the camera image
    resize(camera_image, camera_image, new_size);
	
// Convert the camera image to grayscale
    cvtColor(camera_image, camera_image, COLOR_BGR2GRAY);

    // Compare the camera image with the two images
    Mat difference1, difference2;
    absdiff(camera_image, image1, difference1);
    absdiff(camera_image, image2, difference2);
    // Put text on the camera image with the comparison result

    if (countNonZero(difference1)< countNonZero(difference1)||countNonZero(difference1)<countNonZero(difference2))

    {
        putText(camera_image,"Conhecido", Point(20, 30), FONT_HERSHEY_SIMPLEX, 1, Scalar(0, 255, 0), 2);
    // Save the labeled camera image
      // +++++++++++++++++        
        strcpy(varNome,"Conhecido");
      // +++++++++++++++++        
         {
            strcpy(str1, "/home/alisson/Documentos/Trabalho_Final/capturas/SOE_Projeto_final/capturaImagens/imagem_conhecido");
            strcat(str1, nomeData());
            strcat(str1,".jpg");
         }
        imwrite(str1,camera_image);
    }

    else
    {
        putText(camera_image, "Desconhecido", Point(20, 30), FONT_HERSHEY_SIMPLEX, 1, Scalar(0, 255, 0), 2);
  // +++++++++++++++++ 
        strcpy(varNome,"Desconhecido");
  // +++++++++++++++++        
    // Save the labeled camera image
    {
    strcpy(str1, "/home/alisson/Documentos/Trabalho_Final/capturas/SOE_Projeto_final/capturaImagens/imagem_desconhecido");
    strcat(str1, nomeData());
    strcat(str1,".jpg");
    }
        imwrite(str1,camera_image);
    fprintf(relatorio_acesso.csv,"teste, acesso, %d\r\n",camera_image);    
	}
		
	
    // Show the camera image with the comparison result
    imshow("Camera Image", camera_image);

    // Check if the user pressed the 'q' key
    if (waitKey(1) == 'q')
    {
        stop_capture = true;
    }
}
  // +++++++++++++++++ Escrevendo no CSV +++++++++++++++++++
    std::string csvFile = "/home/alisson/Documentos/Trabalho_Final/capturas/SOE_Projeto_final/capturaImagens/registrocam.csv";
    if(!fileExists(csvFile))
        addArqCSV(csvFile, "Nome", "Data", "Local", "pathImg");

    if (!addArqCSV(csvFile, varNome, nomeData(), "Sala", str1)) {
        std::cerr << "Failed to write to file: " << csvFile << "\n";
    }

return 0;
}
	
