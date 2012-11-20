# -*- Mode: Python; test-case-name: morituri.test.test_result_logger -*-
# vi:si:et:sw=4:sts=4:ts=4

# Morituri - for those about to RIP

# Copyright (C) 2009 Thomas Vander Stichele

# This file is part of morituri.
#
# morituri is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# morituri is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with morituri.  If not, see <http://www.gnu.org/licenses/>.

import time

from morituri.common import common
from morituri.configure import configure


class MorituriLogger(object):

    def log(self, ripResult, epoch=time.time()):
        lines = self.logRip(ripResult, epoch=epoch)
        return '\n'.join(lines)

    def logRip(self, ripResult, epoch):

        lines = []

        ### global

        lines.append("morituri version %s" % configure.version)
        lines.append("")
        # FIXME: when we localize this, see #49 to handle unicode properly.
        import locale
        old = locale.getlocale(locale.LC_TIME)
        locale.setlocale(locale.LC_TIME, 'C')
        date = time.strftime("%b %d %H:%M:%S", time.localtime(epoch))
        locale.setlocale(locale.LC_TIME, old)
        lines.append("morituri logfile from %s" % date)
        lines.append("")

        # album
        lines.append("%s / %s" % (ripResult.artist, ripResult.title))
        lines.append("")

        # drive
        lines.append(
            "Used Drive  : %s %s %s" % (
                ripResult.vendor, ripResult.model, ripResult.release))
        lines.append("")

        # Default for cdparanoia
        lines.append("Use cdparanoia mode      : Yes (%s)" % (
            ripResult.cdparanoia_version))

        # Default for cdparanoia by virtue of ripping whole tracks at a time
        lines.append("Defeat audio cache       : Yes")

        # Default for cdparanoia by virtue of having no C2 rip mode
        lines.append("Make use of C2 pointers  : No")

        lines.append("")
        lines.append("Read offset correction                      : %d" % (
            ripResult.offset))

        # Currently unsupported by cdparanoia
        lines.append("Overread into Lead-In and Lead-Out          : No")

        # Default for cdparanoia
        lines.append("Fill up missing offset samples with silence : Yes")

        # Default for cdparanoia
        lines.append("Delete leading and trailing silent blocks   : No")

        # Default
        lines.append("Null samples used in CRC calculations       : Yes")

        lines.append("Gap Detection                               : "
            "cdrdao version %s" % ripResult.cdrdao_version)
            
        # Default for cdparanoia
        lines.append("Gap handling                                : "
            "Appended to previous track")
        lines.append("")

        # toc
        lines.append("TOC of the extracted CD")
        lines.append("")
        lines.append(
            "     Track |   Start  |  Length  | Start sector | End sector")
        lines.append(
            "    ---------------------------------------------------------")
        table = ripResult.table


        for t in table.tracks:
            start = t.getIndex(1).absolute
            length = table.getTrackLength(t.number)
            lines.append(
            "       %2d  | %s | %s | %9d    | %8d" % (
                t.number,
                common.framesToMSF(start),
                common.framesToMSF(length),
                start,
                start + length - 1))

        lines.append("")
        lines.append("")

        ### per-track
        for t in ripResult.tracks:
            lines.extend(self.trackLog(t))
            lines.append('')

        return lines

    def trackLog(self, trackResult):

        lines = []

        lines.append('Track %2d' % trackResult.number)
        lines.append('')
        lines.append('     Filename %s' % trackResult.filename)
        lines.append('')
        if trackResult.pregap:
            lines.append('     Pre-gap length %s' % common.framesToMSF(
                trackResult.pregap))
            lines.append('')

        lines.append('     Peak level %.06f' % trackResult.peak)
        if trackResult.testspeed:
            lines.append('     Extraction Speed (Test) %.4f X' % (
                trackResult.testspeed))
        if trackResult.copyspeed:
            lines.append('     Extraction Speed (Copy) %.4f X' % (
                trackResult.copyspeed))
        if trackResult.testcrc:
            lines.append('     Test CRC %08X' % trackResult.testcrc)
        if trackResult.copycrc:
            lines.append('     Copy CRC %08X' % trackResult.copycrc)
        if trackResult.ARCRC:
            lines.append('     AccurateRip signature %08X' % trackResult.ARCRC)

        if trackResult.accurip:
            lines.append('     Accurately ripped (confidence %d)' % (
                trackResult.ARDBConfidence))
        else:
            if trackResult.ARDBCRC:
                lines.append('     Cannot be verified as accurate, '
                    'AccurateRip returned [%08X]' % (
                        trackResult.ARDBCRC))
            else:
                lines.append('     Track not present in AccurateRip database')

        if trackResult.testcrc:
            if trackResult.testcrc == trackResult.copycrc:
                lines.append('     Copy OK')
            else:
                lines.append("     WARNING: CRCs don't match!")
        else:
            lines.append("     WARNING: no CRC check done")

        return lines
