from app import external

if __name__ == "__main__":
    ret, rank1, rank2, rank3, output = external.build_function('/vagrant/app/static/uploads/acnazarejr_1cd947fe29fa4d9b84f2e529b524d4e8.zip', '/vagrant/app/static/images', '/vagrant/app/static/comparacao')
    print(ret)
    print(rank1)
    print(rank2)
    print(rank3)
    print(output)
