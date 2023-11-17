from kalinan_bot import KalinanBot
from kalinan import Kalinan

if __name__ == '__main__':
    kalinan_instanse = Kalinan()
    kn = KalinanBot(kalinan_instanse=kalinan_instanse)
    kn.run()