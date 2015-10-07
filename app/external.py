from flask import current_app
from . import db
from .models import Build, BuildStatus
from random import random
import os


def run_builds():
    return
    # build = Build.query.filter_by(status=0).first()
    # if build is not None:
    #     uploads_folder = os.path.join(current_app.config['APP_ROOT'], 'static', current_app.config['UPLOAD_FOLDER'])
    #     build_file_path = uploads_folder + "/" + build.build_hash + ".zip"
    #
    #     if not os.path.isfile(build_file_path):
    #         print("error 1")
    #         build.status = BuildStatus.ERROR
    #         db.session.commit()
    #         return
    #
    #     # William's function
    #     build.status = BuildStatus.BUILD
    #     db.session.commit()
    #     rank1, rank2, rank3 = build_function(build_file_path)
    #
    #     log_file_path = uploads_folder + "/" + build.build_hash + ".txt"
    #     log_file = open(log_file_path, "w")
    #     for i in range(0, 30):
    #         log_file.write("build for: " + build.build_hash + "\n")
    #     log_file.close()
    #
    #     build.status = BuildStatus.SUCCESS
    #     build.rank1 = rank1
    #     build.rank2 = rank2
    #     build.rank3 = rank3
    #     db.session.commit()
    # print(build)


def build_function(build_file):
    rank1 = random() * 10
    rank2 = random() * 10
    rank3 = random() * 10
    return rank1, rank2, rank3


def randomword(length):
    return ''.join(random.choice(string.lowercase) for i in range(length))


def main2(zipfile):

    inputfile = zipfile
    images = ["lena.png", "lena2.png", "lena3.png"]

    directory = randomword(20)
    comparaDir = 'comparacao'

    print
    "\n--- Compiling ---\n"
    script = 'mkdir ' + directory + ' && ' + \
             'unzip -j ' + inputfile + ' -d ' + directory + ' && ' + \
             'cd ' + directory + ' && ' + \
             'make;'

    ret = subprocess.call(script, shell=True)
    if ret != 0:
        return None

    import time

    totalInSize = 0
    totalCompressSize = 0
    totalTime = 0
    totalPSNR = 0
    for i in range(len(images)):
        image = images[i]

        print
        "\n--- Image %d/%d (%s) ---" % (i + 1, len(images), image)

        img = Image.open(image)
        wid, hei = img.size
        totalsize = wid * hei
        print
        "Original image size: %dx%d (%d bytes)" % (wid, hei, totalsize)
        totalInSize = totalInSize + totalsize

        script2 = 'cp ' + image + ' ' + directory + ' && ' + \
                  'cd ' + directory + ' && ' + \
                  'rm -f psnr.txt && ' + \
                  './compacta ' + image

        start_time = time.time()
        ret = subprocess.call(script2, shell=True)
        totalTime = totalTime + time.time() - start_time

        if ret != 0:
            return None

        filenoExt = os.path.splitext(image)[0]
        fileComp = filenoExt + '.compactado'
        fileRec = filenoExt + '.saida.png'


        # get compressed size
        imsize = os.path.getsize(directory + '/' + fileComp)
        print
        "Compressed image size: %d bytes" % (imsize)
        totalCompressSize = totalCompressSize + imsize

        script3 = 'cd ' + directory + ' && ' + \
                  './descompacta ' + fileComp

        start_time = time.time()
        ret = subprocess.call(script3, shell=True)
        totalTime = totalTime + time.time() - start_time

        if ret != 0:
            return None

        script4 = 'cp ' + directory + '/' + fileRec + ' ' + comparaDir + ' && ' + \
                  'cp ' + image + ' ./comparacao && ' + \
                  'cd ' + comparaDir + ' && ' + \
                  './compara ' + image + ' ' + fileRec + ' && ' + \
                  'rm ' + image + ' && ' + \
                  'rm ' + fileRec + '; '

        ret = subprocess.call(script4, shell=True)

        if ret != 0:
            return None

        f = open(comparaDir + '/psnr.txt', 'r')
        value = f.readline();

        psnr = float(value)

        print
        "CR: %5.3f" % (float(totalsize) / float(imsize))
        print
        "PSNR: %5.3f" % (psnr)

        totalPSNR = totalPSNR + psnr;

    shutil.rmtree(directory)

    CR = float(totalInSize) / float(totalCompressSize)

    psnr = float(totalPSNR) / float(len(images))

    print("\n\n---- Execution summary ----")
    print("Total time: %5.3f seconds" % totalTime)
    print("Average compression ratio: %5.3f" % CR)
    print("Average PSNR: %5.3f" % psnr)

    time = totalTime

    return psnr, time, CR
