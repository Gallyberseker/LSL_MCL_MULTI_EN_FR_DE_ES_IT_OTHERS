"""Fonctions du domaine IMAGES pour Larry MCL."""
from pathlib import Path
from PIL import Image
import io
import mmap
import struct
import LSL_MCL_VARIABLES as V
from LSL_MCL_VARIABLES import *  # Paramètres utilisés aussi dans les arguments par défaut.
import LSL_MCL_JAMS
import LSL_MCL_ROUTAGE

class LSL_MCL_Images:
    """Opérations images du modèle."""

    @staticmethod
    def dossier_image_classee(racine, format_image, largeur, hauteur):
        """
        Retourne automatiquement le dossier correspondant
        au format et aux dimensions exactes de l'image.

        Exemple :
            BMP 32x32   -> BMP/32x32
            BMP 256x128 -> BMP/256x128
            DDS 640x448 -> DDS/640x448
            ICO 16x16   -> ICO/16x16
        """
        format_image = str(format_image).upper()

        dossier = racine / format_image

        if largeur > 0 and hauteur > 0:
            dossier = dossier / f"{largeur}x{hauteur}"

        return dossier


    @staticmethod
    def chemin_image_classee(racine, format_image, largeur, hauteur, nom):
        """Construit le chemin complet d'une image classée."""
        return LSL_MCL_Images.dossier_image_classee(
            racine, format_image, largeur, hauteur
        ) / nom


    @staticmethod
    def creer_dossiers_images(racine):
        """
        Crée uniquement les dossiers principaux des formats.

        Les sous-dossiers de dimensions sont créés automatiquement
        lorsqu'une image est réellement rencontrée.
        """
        for format_image in V.FORMATS_IMAGES:
            (racine / format_image).mkdir(
                parents=True,
                exist_ok=True
            )


    @staticmethod
    def dimensions_pillow(bloc):
        """
        Implémente le traitement interne `dimensions_pillow` utilisé par le pipeline de localisation ou de diagnostic.
    
        Paramètres:
            bloc.
    
        Connexions:
            Appelée par : gif_valide, ico_valide, jpg_valide, webp_valide.
            Appelle : aucune autre fonction interne directe détectée.
        """
        try:

            with Image.open(io.BytesIO(bloc)) as image:

                return image.size

        except Exception:

            return None


    @staticmethod
    def bmp_valide(data, pos):
        """
        Implémente le traitement interne `bmp_valide` utilisé par le pipeline de localisation ou de diagnostic.
    
        Paramètres:
            data, pos.
    
        Connexions:
            Appelée par : aucun appel direct statiquement détecté (point d'entrée, callback ou appel dynamique possible).
            Appelle : aucune autre fonction interne directe détectée.
        """
        if (pos + 26 > len(data) or data[pos:pos + 2] != b"BM"):
            return None

        try:

            taille = struct.unpack_from("<I", data, pos + 2)[0]

            dib = struct.unpack_from("<I", data, pos + 14)[0]

            if dib == 12:

                w = struct.unpack_from("<H", data, pos + 18)[0]

                h = struct.unpack_from("<H", data, pos + 20)[0]

                bpp = struct.unpack_from("<H", data, pos + 24)[0]

                compression = 0

            else:

                if pos + 54 > len(data):
                    return None

                w = abs(struct.unpack_from("<i", data, pos + 18)[0])

                h = abs(struct.unpack_from("<i", data, pos + 22)[0])

                bpp = struct.unpack_from("<H", data, pos + 28)[0]

                compression = struct.unpack_from("<I", data, pos + 30)[0]

        except struct.error:
            return None

        if dib not in (12, 40, 52, 56, 108, 124):
            return None

        if bpp not in (1, 4, 8, 16, 24, 32):
            return None

        if not (1 <= w <= 8192 and 1 <= h <= 8192):
            return None

        if (taille < 26 or pos + taille > len(data)):
            return None

        return {
            "format": "BMP",
            "extension": ".bmp",
            "taille": taille,
            "largeur": w,
            "hauteur": h,
            "bpp": bpp,
            "compression": compression,
            "description": f"{w}x{h}__{bpp}bpp",
        }


    @staticmethod
    def dds_valide(data, pos):
        """
        Implémente le traitement interne `dds_valide` utilisé par le pipeline de localisation ou de diagnostic.
    
        Paramètres:
            data, pos.
    
        Connexions:
            Appelée par : aucun appel direct statiquement détecté (point d'entrée, callback ou appel dynamique possible).
            Appelle : aucune autre fonction interne directe détectée.
        """
        if (pos + 128 > len(data) or data[pos:pos + 4] != b"DDS "):
            return None

        try:

            header = struct.unpack_from("<I", data, pos + 4)[0]

            h = struct.unpack_from("<I", data, pos + 12)[0]

            w = struct.unpack_from("<I", data, pos + 16)[0]

            mipmaps = max(1, struct.unpack_from("<I", data, pos + 28)[0])

            pf = struct.unpack_from("<I", data, pos + 76)[0]

            fourcc = data[pos + 84:pos + 88]

        except struct.error:
            return None

        if header != 124 or pf != 32:
            return None

        bloc8 = (
            b"DXT1",
            b"ATI1",
            b"BC4U",
            b"BC4S",
        )

        bloc16 = (
            b"DXT3",
            b"DXT5",
            b"ATI2",
            b"BC5U",
            b"BC5S",
        )

        if fourcc in bloc8:
            bloc = 8

        elif fourcc in bloc16:
            bloc = 16

        else:
            return None

        if not (1 <= w <= 8192 and 1 <= h <= 8192):
            return None

        taille = 128

        mw = w
        mh = h

        for _ in range(mipmaps):

            taille += (max(1, (mw + 3) // 4) * max(1, (mh + 3) // 4) * bloc)

            mw = max(1, mw // 2)

            mh = max(1, mh // 2)

        if pos + taille > len(data):
            return None

        fmt = fourcc.decode("ascii", errors="replace")

        return {
            "format": "DDS",
            "extension": ".dds",
            "taille": taille,
            "largeur": w,
            "hauteur": h,
            "fourcc": fmt,
            "mipmaps": mipmaps,
            "description": f"{w}x{h}__{fmt}",
        }


    @staticmethod
    def jpg_valide(data, pos):
        """
        Implémente le traitement interne `jpg_valide` utilisé par le pipeline de localisation ou de diagnostic.
    
        Paramètres:
            data, pos.
    
        Connexions:
            Appelée par : aucun appel direct statiquement détecté (point d'entrée, callback ou appel dynamique possible).
            Appelle : dimensions_pillow.
        """
        if (data[pos:pos + 3] != b"\xFF\xD8\xFF"):
            return None

        fin = data.find(b"\xFF\xD9", pos + 3)

        if fin < 0:
            return None

        taille = (fin + 2 - pos)

        if taille < 100:
            return None

        dim = LSL_MCL_Images.dimensions_pillow(data[pos:pos + taille])

        if not dim:
            return None

        w, h = dim

        return {
            "format": "JPG",
            "extension": ".jpg",
            "taille": taille,
            "largeur": w,
            "hauteur": h,
            "description": f"{w}x{h}",
        }


    @staticmethod
    def png_valide(data, pos):
        """
        Implémente le traitement interne `png_valide` utilisé par le pipeline de localisation ou de diagnostic.
    
        Paramètres:
            data, pos.
    
        Connexions:
            Appelée par : aucun appel direct statiquement détecté (point d'entrée, callback ou appel dynamique possible).
            Appelle : aucune autre fonction interne directe détectée.
        """
        signature = (b"\x89PNG\r\n\x1a\n")

        if (data[pos:pos + 8] != signature):
            return None

        if pos + 24 > len(data):
            return None

        try:

            w, h = struct.unpack_from(">II", data, pos + 16)

        except struct.error:
            return None

        p = pos + 8

        while p + 12 <= len(data):

            longueur = struct.unpack_from(">I", data, p)[0]

            type_chunk = data[p + 4:p + 8]

            p += longueur + 12

            if p > len(data):
                return None

            if type_chunk == b"IEND":

                return {
                    "format": "PNG",
                    "extension": ".png",
                    "taille": p - pos,
                    "largeur": w,
                    "hauteur": h,
                    "description": f"{w}x{h}",
                }

        return None


    @staticmethod
    def webp_valide(data, pos):
        """
        Implémente le traitement interne `webp_valide` utilisé par le pipeline de localisation ou de diagnostic.
    
        Paramètres:
            data, pos.
    
        Connexions:
            Appelée par : aucun appel direct statiquement détecté (point d'entrée, callback ou appel dynamique possible).
            Appelle : dimensions_pillow.
        """
        if pos + 12 > len(data):
            return None

        if (data[pos:pos + 4] != b"RIFF" or data[pos + 8:pos + 12] != b"WEBP"):
            return None

        taille = (struct.unpack_from("<I", data, pos + 4)[0] + 8)

        if (taille < 16 or pos + taille > len(data)):
            return None

        dim = LSL_MCL_Images.dimensions_pillow(data[pos:pos + taille])

        if not dim:
            return None

        return {
            "format": "WEBP",
            "extension": ".webp",
            "taille": taille,
            "largeur": dim[0],
            "hauteur": dim[1],
            "description": f"{dim[0]}x{dim[1]}",
        }


    @staticmethod
    def gif_valide(data, pos):
        """
        Implémente le traitement interne `gif_valide` utilisé par le pipeline de localisation ou de diagnostic.
    
        Paramètres:
            data, pos.
    
        Connexions:
            Appelée par : aucun appel direct statiquement détecté (point d'entrée, callback ou appel dynamique possible).
            Appelle : dimensions_pillow.
        """
        if data[pos:pos + 6] not in (b"GIF87a", b"GIF89a"):
            return None

        recherche = pos + 13

        while True:

            fin = data.find(b"\x3B", recherche)

            if fin < 0:
                return None

            taille = (fin + 1 - pos)

            dim = LSL_MCL_Images.dimensions_pillow(data[pos:pos + taille])

            if dim:

                return {
                    "format": "GIF",
                    "extension": ".gif",
                    "taille": taille,
                    "largeur": dim[0],
                    "hauteur": dim[1],
                    "description": f"{dim[0]}x{dim[1]}",
                }

            recherche = fin + 1


    @staticmethod
    def ico_valide(data, pos):
        """
        Implémente le traitement interne `ico_valide` utilisé par le pipeline de localisation ou de diagnostic.
    
        Paramètres:
            data, pos.
    
        Connexions:
            Appelée par : aucun appel direct statiquement détecté (point d'entrée, callback ou appel dynamique possible).
            Appelle : dimensions_pillow.
        """
        if (data[pos:pos + 4] != b"\x00\x00\x01\x00"):
            return None

        if pos + 6 > len(data):
            return None

        nombre = struct.unpack_from("<H", data, pos + 4)[0]

        if not (1 <= nombre <= 256):
            return None

        max_fin = 0

        for index in range(nombre):

            p = (pos + 6 + index * 16)

            if p + 16 > len(data):
                return None

            taille = struct.unpack_from("<I", data, p + 8)[0]

            offset = struct.unpack_from("<I", data, p + 12)[0]

            max_fin = max(max_fin, offset + taille)

        if (max_fin < 22 or pos + max_fin > len(data)):
            return None

        dim = LSL_MCL_Images.dimensions_pillow(data[pos:pos + max_fin])

        if not dim:
            return None

        return {
            "format": "ICO",
            "extension": ".ico",
            "taille": max_fin,
            "largeur": dim[0],
            "hauteur": dim[1],
            "description": f"{dim[0]}x{dim[1]}",
        }


    @staticmethod
    def image_valide(chemin):
        """
        VALIDATEUR CENTRAL DES IMAGES EXTRAITES.

        Reconnecte tous les validateurs spécialisés du moteur :
            BMP       -> bmp_valide()
            DDS       -> dds_valide()
            JPG/JPEG  -> jpg_valide()
            PNG       -> png_valide()
            WEBP      -> webp_valide()
            GIF       -> gif_valide()
            ICO       -> ico_valide()

        Le fichier réellement écrit sur le disque est relu puis contrôlé.
        Retourne les informations du validateur si l'image est correcte,
        sinon None.
        """
        chemin = Path(chemin)

        if not chemin.is_file():
            return None

        try:
            data = chemin.read_bytes()
        except OSError:
            return None

        if not data:
            return None

        validateurs = {
            ".bmp": LSL_MCL_Images.bmp_valide,
            ".dds": LSL_MCL_Images.dds_valide,
            ".jpg": LSL_MCL_Images.jpg_valide,
            ".jpeg": LSL_MCL_Images.jpg_valide,
            ".png": LSL_MCL_Images.png_valide,
            ".webp": LSL_MCL_Images.webp_valide,
            ".gif": LSL_MCL_Images.gif_valide,
            ".ico": LSL_MCL_Images.ico_valide,
        }

        validateur = validateurs.get(chemin.suffix.lower())

        if validateur is None:
            return None

        try:
            information = validateur(data, 0)
        except (OSError, ValueError, TypeError, struct.error):
            return None

        if not information:
            return None

        # L'extraction doit correspondre exactement à l'image détectée.
        # Cela détecte aussi les fichiers tronqués ou suivis de données parasites.
        if information.get("taille") != len(data):
            return None

        return information


    @staticmethod
    def scanner_images_jam_mmap(jam, jam_root):
        """
        Implémente le traitement interne `scanner_images_jam_mmap` utilisé par le pipeline de localisation ou de diagnostic.
    
        Paramètres:
            jam, jam_root.
    
        Connexions:
            Appelée par : extraire_images.
            Appelle : aucune autre fonction interne directe détectée.
        """

        candidats = []
        inconnus = []

        if jam.stat().st_size == 0:
            return candidats, inconnus

        with jam.open("rb") as flux:

            with mmap.mmap(flux.fileno(), 0, access=mmap.ACCESS_READ) as data:

                for correspondance in V.SIGNATURES_IMAGES_RE.finditer(data):

                    signature = correspondance.group(0)
                    position = correspondance.start()
                    detecteur = V.DETECTEURS_PAR_SIGNATURE[signature]
                    information = detecteur(data, position)

                    if information:
                        candidats.append((position, information))

                for correspondance in V.SIGNATURES_INCONNUES_RE.finditer(data):

                    signature = correspondance.group(0)
                    position = correspondance.start()

                    inconnus.append({
                        "jam": str(jam.relative_to(jam_root)),
                        "type": V.SIGNATURES_INCONNUES[signature],
                        "offset": position,
                        "offset_hex": f"0x{position:08X}",
                    })

        return candidats, inconnus


    @staticmethod
    def nom_image_ps2_normalise(jam, jam_root, index_jam_pc):
        """
        Normalise UNIQUEMENT le préfixe du nom des images extraites PS2.

        Exemple :
            PS2__LOADSCRN.JAM__BMP__0019__004881D4__512x512__8bpp.bmp
            ->
            LoadScrn.JAM__BMP__0019__004881D4__512x512__8bpp.bmp

        Aucun fichier JAM source n'est renommé.
        """
        relatif_ps2 = LSL_MCL_JAMS.LSL_MCL_jams.nom_jam(jam, jam_root)

        # L'ancien extracteur pouvait préfixer le nom logique par PS2__.
        # Ce préfixe ne doit jamais apparaître dans le nom final de l'image.
        while relatif_ps2.upper().startswith("PS2__"):
            relatif_ps2 = relatif_ps2[5:]

        # Reprend automatiquement la casse exacte utilisée par le JAM PC.
        # Ex. LOADSCRN.JAM -> LoadScrn.JAM
        return index_jam_pc.get(
            relatif_ps2.casefold(),
            relatif_ps2
        )


    @staticmethod
    def normaliser_bmp_image(image, original):
        """
        Normalise bmp image.
    
        Paramètres:
            image, original.
    
        Connexions:
            Appelée par : normaliser_bmp.
            Appelle : aucune autre fonction interne directe détectée.
        """
        template = bytearray(original)

        if template[:2] != b"BM":

            raise ValueError("BMP original invalide")

        dib = struct.unpack_from("<I", template, 14)[0]

        if dib < 40:

            raise ValueError("BMP ancien : fournir un BMP "
                             "de taille binaire identique")

        offset = struct.unpack_from("<I", template, 10)[0]

        largeur = abs(struct.unpack_from("<i", template, 18)[0])

        hauteur_brute = (struct.unpack_from("<i", template, 22)[0])

        hauteur = abs(hauteur_brute)

        bpp = struct.unpack_from("<H", template, 28)[0]

        compression = struct.unpack_from("<I", template, 30)[0]

        if compression != 0:

            raise ValueError(f"BMP compresse {compression}")

        if image.size != (largeur, hauteur):

            raise ValueError(f"dimensions {image.size} != "
                             f"{largeur}x{hauteur}")

        stride = ((largeur * bpp + 31) // 32) * 4

        zone = (stride * hauteur)

        if (offset + zone > len(template)):

            raise ValueError("Zone pixels BMP invalide")

        bas_haut = (hauteur_brute > 0)

        pixels_sortie = bytearray(zone)

        if bpp == 24:

            img = image.convert("RGB")

            px = img.load()

            for ligne in range(hauteur):

                y = (hauteur - 1 - ligne if bas_haut else ligne)

                dest = (ligne * stride)

                for x in range(largeur):

                    r, g, b = px[x, y]

                    p = (dest + x * 3)

                    pixels_sortie[p:p + 3] = bytes((b, g, r))

        elif bpp == 32:

            img = image.convert("RGBA")

            px = img.load()

            for ligne in range(hauteur):

                y = (hauteur - 1 - ligne if bas_haut else ligne)

                dest = (ligne * stride)

                for x in range(largeur):

                    r, g, b, a = (px[x, y])

                    p = (dest + x * 4)

                    pixels_sortie[p:p + 4] = bytes((b, g, r, a))

        elif bpp == 8:

            palette_debut = (14 + dib)

            palette_octets = (offset - palette_debut)

            couleurs = min(256, palette_octets // 4)

            if couleurs < 2:

                raise ValueError("Palette BMP invalide")

            q = image.convert("RGB").quantize(colors=couleurs,
                                              method=(Image.Quantize.MEDIANCUT),
                                              dither=(Image.Dither.FLOYDSTEINBERG))

            palette = q.getpalette()

            for index in range(couleurs):

                r = palette[index * 3]

                g = palette[index * 3 + 1]

                b = palette[index * 3 + 2]

                p = (palette_debut + index * 4)

                template[p:p + 4] = bytes((b, g, r, 0))

            brut = q.tobytes()

            for ligne in range(hauteur):

                y = (hauteur - 1 - ligne if bas_haut else ligne)

                src = (y * largeur)

                dst = (ligne * stride)

                pixels_sortie[dst:dst + largeur] = brut[src:src + largeur]

        else:

            raise ValueError(f"BMP {bpp}bpp : "
                             "conversion automatique non geree")

        template[offset:offset + zone] = pixels_sortie

        return bytes(template)


    @staticmethod
    def normaliser_bmp(fichier, original):
        """
        Normalise bmp.
    
        Paramètres:
            fichier, original.
    
        Connexions:
            Appelée par : injecter_ecran_sierra_localise, injecter_images.
            Appelle : normaliser_bmp_image.
        """
        if (fichier.suffix.lower() == ".bmp"):

            brut = fichier.read_bytes()

            if len(brut) == len(original):

                try:

                    img = Image.open(io.BytesIO(brut))

                    if img.size == Image.open(io.BytesIO(original)).size:

                        return brut

                except Exception:
                    pass

        with Image.open(fichier) as image:

            return LSL_MCL_Images.normaliser_bmp_image(image, original)


    @staticmethod
    def rgb565(r, g, b):
        """
        Convertit une couleur vers RGB565.
    
        Paramètres:
            r, g, b.
    
        Connexions:
            Appelée par : bloc_couleur.
            Appelle : aucune autre fonction interne directe détectée.
        """
        return (((r * 31 + 127) // 255) << 11
                | ((g * 63 + 127) // 255) << 5
                | ((b * 31 + 127) // 255))


    @staticmethod
    def rgb565_inverse(c):
        """
        Convertit une couleur vers RGB565 inverse.
    
        Paramètres:
            c.
    
        Connexions:
            Appelée par : palette_couleur.
            Appelle : aucune autre fonction interne directe détectée.
        """
        return (
            ((c >> 11) & 31) * 255 // 31,
            ((c >> 5) & 63) * 255 // 63,
            (c & 31) * 255 // 31,
        )


    @staticmethod
    def palette_couleur(c0, c1, transparent):
        """
        Implémente le traitement interne `palette_couleur` utilisé par le pipeline de localisation ou de diagnostic.
    
        Paramètres:
            c0, c1, transparent.
    
        Connexions:
            Appelée par : bloc_couleur.
            Appelle : rgb565_inverse.
        """
        a = LSL_MCL_Images.rgb565_inverse(c0)

        b = LSL_MCL_Images.rgb565_inverse(c1)

        if transparent:

            c2 = tuple((a[i] + b[i]) // 2 for i in range(3))

            return [
                a,
                b,
                c2,
                (0, 0, 0),
            ]

        c2 = tuple((2 * a[i] + b[i]) // 3 for i in range(3))

        c3 = tuple((a[i] + 2 * b[i]) // 3 for i in range(3))

        return [
            a,
            b,
            c2,
            c3,
        ]


    @staticmethod
    def bloc_couleur(pixels, autoriser_transparence):
        """
        Implémente le traitement interne `bloc_couleur` utilisé par le pipeline de localisation ou de diagnostic.
    
        Paramètres:
            pixels, autoriser_transparence.
    
        Connexions:
            Appelée par : encoder_dxt.
            Appelle : palette_couleur, rgb565.
        """
        transparent = (autoriser_transparence
                       and any(a < 128 for _, _, _, a in pixels))

        couleurs = [(r, g, b) for r, g, b, a in pixels
                    if (not transparent or a >= 128)]

        if not couleurs:
            couleurs = [(0, 0, 0)]

        sombre = min(couleurs, key=lambda c: sum(c))

        clair = max(couleurs, key=lambda c: sum(c))

        c0 = LSL_MCL_Images.rgb565(*clair)

        c1 = LSL_MCL_Images.rgb565(*sombre)

        if transparent:

            if c0 > c1:
                c0, c1 = c1, c0

        else:

            if c0 < c1:
                c0, c1 = c1, c0

            elif c0 == c1:
                if c0 < 65535:
                    c0 += 1
                else:
                    c1 -= 1

            if c0 <= c1:
                raise RuntimeError(
                    "Bloc DXT opaque invalide : c0 doit être supérieur à c1.")

        palette = LSL_MCL_Images.palette_couleur(c0, c1, transparent)

        bits = 0

        for index, pixel in enumerate(pixels):

            r, g, b, a = pixel

            if (transparent and a < 128):
                choix = 3

            else:

                limite = (3 if transparent else 4)

                choix = min(range(limite),
                            key=lambda i: (r - palette[i][0])**2 +
                            (g - palette[i][1])**2 + (b - palette[i][2])**2)

            bits |= (choix << (index * 2))

        return struct.pack("<HHI", c0, c1, bits)


    @staticmethod
    def pixels_bloc(image, bx, by):
        """
        Implémente le traitement interne `pixels_bloc` utilisé par le pipeline de localisation ou de diagnostic.
    
        Paramètres:
            image, bx, by.
    
        Connexions:
            Appelée par : encoder_dxt.
            Appelle : aucune autre fonction interne directe détectée.
        """
        px = image.load()

        return [
            px[min(bx + x, image.width - 1),
               min(by + y, image.height - 1)] for y in range(4) for x in range(4)
        ]


    @staticmethod
    def encoder_dxt(image, fourcc):
        """
        Encode dxt.
    
        Paramètres:
            image, fourcc.
    
        Connexions:
            Appelée par : reconstruire_dds.
            Appelle : alpha_dxt3, alpha_dxt5, bloc_couleur, pixels_bloc.
        """
        sortie = bytearray()

        for y in range(0, image.height, 4):

            for x in range(0, image.width, 4):

                pixels = LSL_MCL_Images.pixels_bloc(image, x, y)

                if fourcc == b"DXT1":

                    sortie += LSL_MCL_Images.bloc_couleur(pixels, True)

                elif fourcc == b"DXT3":

                    sortie += LSL_MCL_Images.alpha_dxt3(pixels)

                    sortie += LSL_MCL_Images.bloc_couleur(pixels, False)

                elif fourcc == b"DXT5":

                    sortie += LSL_MCL_Images.alpha_dxt5(pixels)

                    sortie += LSL_MCL_Images.bloc_couleur(pixels, False)

                else:

                    raise ValueError(f"DDS {fourcc!r} "
                                     "non convertible automatiquement")

        return bytes(sortie)


    @staticmethod
    def infos_dds(data):
        """
        Implémente le traitement interne `infos_dds` utilisé par le pipeline de localisation ou de diagnostic.
    
        Paramètres:
            data.
    
        Connexions:
            Appelée par : reconstruire_dds.
            Appelle : aucune autre fonction interne directe détectée.
        """
        if (len(data) < 128 or data[:4] != b"DDS "):

            raise ValueError("DDS invalide")

        return {
            "largeur": struct.unpack_from("<I", data, 16)[0],
            "hauteur": struct.unpack_from("<I", data, 12)[0],
            "mipmaps": max(1,
                           struct.unpack_from("<I", data, 28)[0]),
            "fourcc": data[84:88],
        }


    @staticmethod
    def reconstruire_dds(fichier, original):
        """
        Implémente le traitement interne `reconstruire_dds` utilisé par le pipeline de localisation ou de diagnostic.
    
        Paramètres:
            fichier, original.
    
        Connexions:
            Appelée par : injecter_images.
            Appelle : encoder_dxt, infos_dds.
        """
        infos = LSL_MCL_Images.infos_dds(original)

        if (fichier.suffix.lower() == ".dds"):

            nouveau = (fichier.read_bytes())

            try:

                ni = LSL_MCL_Images.infos_dds(nouveau)

                if (ni == infos and len(nouveau) == len(original)):

                    return nouveau

            except Exception:
                pass

        fourcc = infos["fourcc"]

        if fourcc not in (
                b"DXT1",
                b"DXT3",
                b"DXT5",
        ):

            raise ValueError(f"{fourcc!r} : "
                             "fournir un DDS deja encode")

        image = Image.open(fichier).convert("RGBA")

        dimensions = (infos["largeur"], infos["hauteur"])

        if image.size != dimensions:

            raise ValueError(f"dimensions {image.size} "
                             f"!= {dimensions}")

        corps = bytearray()
        mip = image

        for niveau in range(infos["mipmaps"]):

            corps += LSL_MCL_Images.encoder_dxt(mip, fourcc)

            if (niveau + 1 < infos["mipmaps"]):

                mip = mip.resize((max(1, mip.width // 2), max(1, mip.height // 2)),
                                 Image.Resampling.LANCZOS)

        resultat = (original[:128] + corps)

        if (len(resultat) != len(original)):

            raise ValueError(f"taille DDS generee "
                             f"{len(resultat)} != "
                             f"{len(original)}")

        return resultat


    @staticmethod
    def remplir_slot(payload, taille):
        """
        Remplit slot.
    
        Paramètres:
            payload, taille.
    
        Connexions:
            Appelée par : encoder_generique.
            Appelle : aucune autre fonction interne directe détectée.
        """
        if len(payload) > taille:

            raise ValueError(f"{len(payload)} octets "
                             f"> slot {taille}")

        return (payload + b"\x00" * (taille - len(payload)))


    @staticmethod
    def encoder_generique(fichier, entree):
        """
        Encode generique.
    
        Paramètres:
            fichier, entree.
    
        Connexions:
            Appelée par : injecter_images.
            Appelle : remplir_slot.
        """
        image = Image.open(fichier)

        dimensions = (entree["largeur"], entree["hauteur"])

        if image.size != dimensions:

            raise ValueError(f"dimensions {image.size} "
                             f"!= {dimensions}")

        fmt = entree["format"]

        limite = entree["taille"]

        essais = []

        if fmt == "JPG":

            image = image.convert("RGB")

            for qualite in range(98, 14, -4):

                buffer = io.BytesIO()

                image.save(buffer,
                           format="JPEG",
                           quality=qualite,
                           optimize=True,
                           progressive=False)

                essais.append(buffer.getvalue())

        elif fmt == "PNG":

            for couleurs in (
                    None,
                    256,
                    128,
                    64,
            ):

                img = image

                if couleurs:

                    img = (image.convert("RGBA").quantize(
                        colors=couleurs, method=(Image.Quantize.FASTOCTREE)))

                buffer = io.BytesIO()

                img.save(buffer, format="PNG", optimize=True, compress_level=9)

                essais.append(buffer.getvalue())

        elif fmt == "GIF":

            buffer = io.BytesIO()

            image.convert("P",
                          palette=(Image.Palette.ADAPTIVE)).save(buffer,
                                                                 format="GIF",
                                                                 optimize=True)

            essais.append(buffer.getvalue())

        elif fmt == "WEBP":

            for qualite in range(98, 14, -4):

                buffer = io.BytesIO()

                image.save(buffer, format="WEBP", quality=qualite, method=6)

                essais.append(buffer.getvalue())

        elif fmt == "ICO":

            buffer = io.BytesIO()

            image.save(buffer, format="ICO")

            essais.append(buffer.getvalue())

        else:

            raise ValueError(f"Format {fmt} non gere")

        possibles = [payload for payload in essais if len(payload) <= limite]

        if not possibles:

            raise ValueError("Impossible de faire tenir "
                             "l'image dans son emplacement")

        meilleur = max(possibles, key=len)

        return LSL_MCL_Images.remplir_slot(meilleur, limite)


    @staticmethod
    def cle_image(nom):
        """
        Implémente le traitement interne `cle_image` utilisé par le pipeline de localisation ou de diagnostic.
    
        Paramètres:
            nom.
    
        Connexions:
            Appelée par : injecter_images.
            Appelle : aucune autre fonction interne directe détectée.
        """
        nom = Path(nom).name

        while (Path(nom).suffix.lower() in V.EXT_IMAGES):

            nom = Path(nom).stem

        return nom.lower()


    @staticmethod
    def alpha_dxt3(pixels):
        """
        Implémente le traitement interne `alpha_dxt3` utilisé par le pipeline de localisation ou de diagnostic.
    
        Paramètres:
            pixels.
    
        Connexions:
            Appelée par : encoder_dxt.
            Appelle : aucune autre fonction interne directe détectée.
        """
        bits = 0

        for index, pixel in enumerate(pixels):

            valeur = (pixel[3] * 15 + 127) // 255

            bits |= (valeur << (index * 4))

        return struct.pack("<Q", bits)


    @staticmethod
    def alpha_dxt5(pixels):
        """
        Implémente le traitement interne `alpha_dxt5` utilisé par le pipeline de localisation ou de diagnostic.
    
        Paramètres:
            pixels.
    
        Connexions:
            Appelée par : encoder_dxt.
            Appelle : alpha_palette_dxt5.
        """
        valeurs = [pixel[3] for pixel in pixels]

        a0 = max(valeurs)
        a1 = min(valeurs)

        if a0 == a1:

            if a0:
                a1 = a0 - 1
            else:
                a0 = 1

        palette = (LSL_MCL_ROUTAGE.LSL_MCL_Routages.alpha_palette_dxt5(a0, a1))

        bits = 0

        for index, alpha in enumerate(valeurs):

            choix = min(range(8), key=lambda i: abs(alpha - palette[i]))

            bits |= (choix << (index * 3))

        return (bytes((a0, a1)) + bits.to_bytes(6, "little"))

