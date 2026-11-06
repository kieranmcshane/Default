"""Extrait un fichier d'un .apkg distant (zip) par requêtes HTTP partielles,
sans télécharger tout le paquet (les médias du Deck EDN - MEA font 1,6 Go,
la base des cartes 15 Mo compressés).

Usage :
  python outils/apkg_distant.py URL                      # liste le contenu
  python outils/apkg_distant.py URL collection.anki21    # extrait la base

URL du Deck EDN - MEA (Drive fourni) :
  https://drive.usercontent.google.com/download?id=1ocZ1MyNf3tOJyXOpxEDUoBMjbwHZe5WG&export=download&confirm=t
"""
import io
import os
import sys
import urllib.request
import zipfile


class FichierDistant(io.RawIOBase):
    def __init__(self, url):
        self.url, self.pos = url, 0
        with urllib.request.urlopen(urllib.request.Request(url, headers={"Range": "bytes=0-0"}), timeout=60) as r:
            self.size = int(r.headers["Content-Range"].split("/")[1])

    def seekable(self):
        return True

    def readable(self):
        return True

    def tell(self):
        return self.pos

    def seek(self, off, whence=0):
        self.pos = off if whence == 0 else self.pos + off if whence == 1 else self.size + off
        return self.pos

    def readinto(self, b):
        if self.pos >= self.size or not len(b):
            return 0
        fin = min(self.pos + len(b), self.size) - 1
        req = urllib.request.Request(self.url, headers={"Range": f"bytes={self.pos}-{fin}"})
        with urllib.request.urlopen(req, timeout=300) as r:
            data = r.read()
        b[:len(data)] = data
        self.pos += len(data)
        return len(data)


def main():
    url, noms = sys.argv[1], sys.argv[2:]
    z = zipfile.ZipFile(io.BufferedReader(FichierDistant(url), buffer_size=1 << 20))
    if not noms:
        for i in z.infolist():
            if not i.filename.isdigit():
                print(i.filename, i.file_size)
        print(len(z.infolist()), "entrées (les noms numériques sont des médias)")
    for nom in noms:
        with z.open(nom) as src, open(nom, "wb") as dst:
            while chunk := src.read(1 << 22):
                dst.write(chunk)
        print("extrait", nom, os.path.getsize(nom))


if __name__ == "__main__":
    main()
