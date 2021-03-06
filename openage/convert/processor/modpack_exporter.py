# Copyright 2020-2020 the openage authors. See copying.md for legal info.

"""
Export data from a modpack to files.
"""
from openage.convert.dataformat.media_types import MediaType
from bin.openage.convert import game_versions


class ModpackExporter:

    @staticmethod
    def export(modpack, assetsrc, exportdir, game_version):
        """
        Export a modpack to a directory.

        :param modpack: Modpack that is going to be exported.
        :type modpack: ..dataformats.modpack.Modpack
        :param exportdir: Directory wheere modpacks are stored.
        :type exportdir: ...util.fslike.path.Path
        """
        modpack_dir = exportdir.joinpath("%s" % (modpack.info.name))

        # Modpack info file
        modpack.info.save(modpack_dir)

        # Data files
        data_files = modpack.get_data_files()

        for data_file in data_files:
            data_file.save(modpack_dir)

        # Media files
        media_files = modpack.get_media_files()

        for media_type in media_files.keys():
            cur_export_requests = media_files[media_type]

            for request in cur_export_requests:
                request.save(assetsrc, modpack_dir, game_version)
