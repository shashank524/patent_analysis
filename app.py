import streamlit as st
import os
from pathlib import Path
from PIL import Image
from pdf2image import convert_from_path
import shutil
import io
from detect import detect
import base64
import zipfile
import glob
from Detector import *


## Helper functions

def _walk(path: Path) -> []:
    all_files = []
    for x in path.iterdir():
        if x.is_dir():
            all_files.extend(_walk(x))
        else:
            all_files.append(x)
    return all_files
def display_images(images_path):
    for file in os.listdir(images_path):
        if file.endswith(".jpg"):
            image = Image.open((images_path+"/"+file))
            st.image(image, caption=file[:-4])

def zip_files(path: Path, archive_name: str):
    all_files = _walk(path)
    with zipfile.ZipFile(f'{archive_name}', 'w', zipfile.ZIP_DEFLATED) as zipf:
        for f in all_files:
            zipf.write(f)
        zipf.close()


def download(file_path, pdf_name):
    zip_ = open(file_path, 'rb').read()

    # readfile = open(file_path,  encoding = "IBM437").read()
    b64 = base64.b64encode(zip_).decode()
    # b64 = base64.b64decode(zip_)
    new_filename = pdf_name+".zip"
    st.markdown(
        "## Generating download link..."

        )
    href = f'<a href="data:file/zip;base64,{b64}" download="{new_filename}">Download Results</a>'
    st.markdown(href, unsafe_allow_html=True)

def detectron2_inference(images_dir, save_dir, detector_):
    for file in os.listdir(images_dir):
        if file.endswith(".jpg"):
            image_name = file[:-4]
            detector_.onImage(
                fileName = file,
                imagePath = (images_dir+'/'+file),
                saveDir=save_dir,
                save_crop=True
            )


# Running the app

def main():
    #Hiding certain elements in production
    hide_streamlit_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>

    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True) 


    st.title("Chem Compound Extractor")
    st.write("""
    ###  Upload a PDF

    """)
    opt = ["v1 (Chemical Compounds)", "v2 (Relavant Structures, Markush Structures, etc)"]
    mode = st.selectbox("", opt) 

    # arr = os.listdir()
    # st.write(arr)
    # Getting PDF from user

    pdf = st.file_uploader("", type="pdf")
    if pdf is not None:

        # Converting PDF to images

        st.write(pdf.name)
        try:
            # The uploaded pdf is in bytes format
            # Inorder to convert it into pages, pdf2image library expects a file path
            # So we need to save the uploaded pdf in a temorary location
            temporarylocation=pdf.name
            with open(temporarylocation,'wb') as out: ## Open temporary file as bytes
                out.write(pdf.read())                ## Read bytes into file

            # st.write(os.getcwd())
            # initialising the path variable
            path = os.getcwd()
            p = Path(path)
            if not p.exists():
                os.mkdir(p)
            PDF_file = path + "/" + pdf.name
            # Finally converting the pdf to images
            if os.path.exists(path+'/pdf_images'):
                shutil.rmtree(path+'/pdf_images')
            os.mkdir(path+'/pdf_images') 
            pages = convert_from_path(PDF_file, dpi=100, grayscale=True) 
            image_counter = 1

            for page in pages: 
                filename = "page_"+str(image_counter)+".jpg"

                # st.write(filename)
                filepath = path+"/pdf_images/" + filename

                page.save(f'{filepath}', 'JPEG') 
                image_counter = image_counter + 1

            filelimit = image_counter-1
        except:
            st.write("Something went wrong...")

        try:
            if mode == opt[0]:

                # YOLOv5 Inference
                save_dir = detect(
                    weights=(path+'/v2_1000.pt'), 
                    source=(path+'/pdf_images'), 
                    line_thickness=2, 
                    conf_thres=0.6, 
                    hide_labels=False, 
                    save_crop=True,
                    project=(path+'/runs/detect'),
                    name=(pdf.name)[:-4]
                )
            else:
                # Detectron2 inference
                save_dir = (path+'/'+pdf.name[:-4])
                if not os.path.exists(save_dir):
                    os.mkdir(save_dir)
                detector = Detector()
                detectron2_inference(
                    detector_ = detector,
                    images_dir = (path+'/pdf_images'),
                    save_dir = (save_dir)
                )

            # st.write(save_dir)
            display_images(str(save_dir))
            st.write("Zipping...")
        except:
            st.write("Something went wrong...")
        
        # Saving the output in a zip file

        try:
            zip_path = path+"/"+(pdf.name[:-4])+".zip"
            # st.write(zip_path)
            # zip_files(Path('runs/detect'), (pdf.name[:-4]+".zip"))
            shutil.make_archive((pdf.name[:-4]), 'zip', save_dir)
            st.write("Done")
        except:
            st.write("Something went wrong ...")
            
        # Cleaning up
        shutil.rmtree(save_dir)
        if os.path.exists(path+"/runs"):
            shutil.rmtree(path+"/runs")
        
        download(zip_path, pdf.name[:-4])

        os.remove(zip_path)
        os.remove(PDF_file)
    else:
        pass
        

if __name__ == "__main__":
    main()