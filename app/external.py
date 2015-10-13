from flask import current_app
from . import db
from .models import Build, BuildStatus
from random import random
import os
import string
import subprocess
import shutil
from PIL import Image
import time


def run_builds():
    build = Build.query.filter_by(status=1).first()
    if build is not None:
        return

    build = Build.query.filter_by(status=0).first()
    if build is not None:
        uploads_folder = os.path.join(current_app.config['APP_ROOT'], 'static', current_app.config['UPLOAD_FOLDER'])
        images_folder = os.path.join(current_app.config['APP_ROOT'], 'static', current_app.config['IMAGES_FOLDER'])
        compara_folder = os.path.join(current_app.config['APP_ROOT'], 'static', current_app.config['COMPARA_FOLDER'])
        build_file_path = uploads_folder + "/" + build.build_hash + ".zip"
        log_file_path = uploads_folder + "/" + build.build_hash + ".txt"
    
        if not os.path.isfile(build_file_path):
            build.status = BuildStatus.ERROR
            db.session.commit()
            return
    
        # William's function
        build.status = BuildStatus.BUILD
        db.session.commit()
        ret, rank1, rank2, rank3, output = build_function(build_file_path, images_folder, compara_folder)
            
        log_file = open(log_file_path, "w")
        log_file.write(output)
        log_file.close()
    
        build.status = BuildStatus.SUCCESS
        build.rank1 = rank1
        build.rank2 = rank2
        build.rank3 = rank3
        db.session.commit()
    print(build)


def before_test(zipfile):
    build_directory = os.path.splitext(zipfile)[0] + '_build'
    if not os.path.exists(build_directory):
        os.makedirs(build_directory)     

    script = 'unzip -j -o ' + zipfile + ' -d ' + build_directory + ' && ' + \
             'cd ' + build_directory + ' && ' + \
             'make;'

    before_test_ret = -1
    before_test_output = '----------------------------------------------\n'
    before_test_output += '[cvContest] Before Running Tests\n'
    before_test_output += '---------------------------------------------\n\n'
    with open('before_test_output', "w") as outfile:
        before_test_ret = subprocess.call(script, shell=True, stdout=outfile)
    with open('before_test_output', "r") as outfile:
        before_test_output += outfile.read()
    os.remove('before_test_output')

    return build_directory, before_test_ret, before_test_output


def compacta(image, i, build_directory):
    script = 'cp ' + image + ' ' + build_directory + ' && ' + \
             'cd ' + build_directory + ' && ' + \
             './compacta ' + image

    compacta_ret = -1
    compacta_output = '----------------------------------------------\n'
    compacta_output += '[cvContest] Compacta for image: ' + str(i) + '\n'
    compacta_output += '---------------------------------------------\n\n'
    with open('compacta_output', "w") as outfile:
        start_time = time.time()
        compacta_ret = subprocess.call(script, shell=True, stdout=outfile)
        compacta_time = time.time() - start_time
    with open('compacta_output', "r") as outfile:
        compacta_output += outfile.read()
    os.remove('compacta_output')

    return compacta_time, compacta_ret, compacta_output


def descompacta(image_comp, i, build_directory):
    script = 'cd ' + build_directory + ' && ' + \
              './descompacta ' + image_comp

    descompacta_ret = -1
    descompacta_output = '----------------------------------------------\n'
    descompacta_output += '[cvContest] Descompacta for image: ' + str(i) + '\n'
    descompacta_output += '---------------------------------------------\n\n'
    with open('descompacta_output', "w") as outfile:
        start_time = time.time()
        descompacta_ret = subprocess.call(script, shell=True, stdout=outfile)
        descompacta_time = time.time() - start_time
    with open('descompacta_output', "r") as outfile:
        descompacta_output += outfile.read()
    os.remove('descompacta_output')

    return descompacta_time, descompacta_ret, descompacta_output


def compara(image, fileRec, i, build_directory, comparaDir):
    script = 'cd ' + comparaDir + ' && ' + \
             './compara ' + image + ' ' + fileRec + '; '
    
    compara_ret = -1
    compara_output = '----------------------------------------------\n'
    compara_output += '[cvContest] Comparacao for image: ' + str(i) + '\n'
    compara_output += '---------------------------------------------\n\n'
    with open('compara_output', "w") as outfile:
        compara_ret = subprocess.call(script, shell=True, stdout=outfile)
    with open('compara_output', "r") as outfile:
        compara_output += outfile.read()
    os.remove('compara_output')

    psnr = -1
    if os.path.exists(comparaDir + '/' + 'psnr.txt'):
        f = open(comparaDir + '/psnr.txt', 'r')
        value = f.readline()
        psnr = float(value)
        f.close()
        os.remove(comparaDir + '/' + 'psnr.txt')        
    else:
        compara_ret = -1

    return psnr, compara_ret, compara_output


def build_function(zipfile, images_folder, compare_directory):
    
    rank_psnr = -1
    rank_time = -1
    rank_cr = -1
    gloabl_output = ''
    global_ret = -1
    images = ["lena.png", "lena2.png", "lena3.png"]  

    build_directory, global_ret, before_test_output = before_test(zipfile)
    gloabl_output += before_test_output
    if global_ret != 0:
        return global_ret, -1, -1, -1, gloabl_output

    totalInSize = 0
    totalCompressSize = 0
    totalTime = 0
    totalPSNR = 0

    for i in range(len(images)):
        image = images_folder + '/' + images[i]

        print("\n--- Image %d/%d (%s) ---" % (i + 1, len(images), image))

        img = Image.open(image)
        wid, hei = img.size
        totalsize = wid * hei
        print("Original image size: %dx%d (%d bytes)" % (wid, hei, totalsize))
        totalInSize = totalInSize + totalsize

        compacta_time, global_ret, compacta_output = compacta(image, i+1, build_directory)
        gloabl_output += compacta_output
        totalTime += compacta_time
        if global_ret != 0:
            return global_ret, -1, -1, -1, gloabl_output

        filenoExt = os.path.splitext(image)[0]
        fileComp = filenoExt + '.compactado'
        fileRec = filenoExt + '.saida.png'

        # get compressed size
        imsize = os.path.getsize(fileComp)
        print("Compressed image size: %d bytes" % (imsize))
        totalCompressSize = totalCompressSize + imsize

        descompacta_time, global_ret, descompacta_output = descompacta(fileComp, i+1, build_directory)
        gloabl_output += descompacta_output
        totalTime += descompacta_time
        if global_ret != 0:
            return global_ret, -1, -1, -1, gloabl_output    

        psnr, global_ret, compara_output = compara(image, fileRec, i, build_directory, compare_directory)
        gloabl_output += compara_output
        if global_ret != 0:
            return global_ret, -1, -1, -1, gloabl_output    

        print("CR: %5.3f" % (float(totalsize) / float(imsize)))
        print("PSNR: %5.3f" % (psnr))

        totalPSNR = totalPSNR + psnr

        if os.path.exists(fileComp):
            os.remove(fileComp)

        if os.path.exists(fileRec):
            os.remove(fileRec)        

    CR = float(totalInSize) / float(totalCompressSize)
    psnr = float(totalPSNR) / float(len(images))

    print("\n\n---- Execution summary ----")
    print("Total time: %5.3f seconds" % totalTime)
    print("Average compression ratio: %5.3f" % CR)
    print("Average PSNR: %5.3f" % psnr)

    rank_psnr = psnr
    rank_cr = CR
    rank_time = totalTime

    # return psnr, time, CR
    return global_ret, rank_psnr, rank_cr, rank_time, gloabl_output
