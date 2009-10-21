#
# client.py - Max Usachev <maxusachev@gmail.com>
#             Ed Bartosh <bartosh@gmail.com>
#             Peter Bienstman <Peter.Bienstman@UGent.be>
#

import os
import base64
import urllib2
import urlparse
from xml.etree import cElementTree

from sync import SyncError
from sync import EventManager
from sync import PROTOCOL_VERSION, N_SIDED_CARD_TYPE


# Overrides get_method method for using PUT request in urllib2.

class PutRequest(urllib2.Request):
    def get_method(self):
        return "PUT"


class Client:

    def __init__(self, url, database, ui):

        """Note: URL contains user and password as well."""

        self.url = urlparse.urlparse(url)
        self.ui = ui
        self.eman = EventManager(database, \
            self.config.mediadir(), self.get_media_file, ui)
        self.id = "TODO"
        self.name = "TODO"
        self.version = "TODO"
        self.deck = "default"
        self.protocol = PROTOCOL_VERSION
        self.cardtypes = N_SIDED_CARD_TYPE
        self.extra = ""
        self.stopped = False

    def start(self):       
        try:
            self.ui.status_bar_message("Authorization. Please wait...")
            self.login_()

            self.ui.status_bar_message("Handshaking. Please wait...")
            self.handshake()

            self.ui.status_bar_message("Creating backup. Please wait...")
            backup_file = self.eman.make_backup()

            server_media_count = self.get_server_media_count()
            if server_media_count:
                self.ui.status_bar_message(\
                    "Applying server media. Please wait...")
                self.eman.apply_media(self.get_media_history(), \
                    server_media_count)

            client_media_count = self.eman.get_media_count()
            if client_media_count:
                self.ui.status_bar_message(\
                    "Sending client media to the server. Please wait...")
                self.send_client_media(self.eman.get_media_history(), \
                    client_media_count)

            server_history_length = self.get_server_history_length()
            if server_history_length:
                self.ui.status_bar_message(\
                    "Applying server history. Please wait...")
                self.get_server_history(server_history_length)

            # Save current database and open backuped database
            # to get history for server.
            self.eman.replace_database(backup_file)
            
            client_history_length = self.eman.get_history_length()
            if client_history_length:
                self.ui.status_bar_message(\
                    "Sending client history to the server. Please wait...")
                self.send_client_history(self.eman.get_history(), \
                    client_history_length)

            # Close temp database and return worked database.
            self.eman.return_databases()

            self.ui.status_bar_message(\
                "Waiting for the server complete. Please, wait...")
    
            self.send_finish_request()

            if self.stopped:
                raise SyncError("Aborted!")
        except SyncError, exception:
            self.eman.restore_backup()
            self.ui.show_message("Error: " + str(exception))
        else:
            self.eman.remove_backup()
            self.ui.show_message("Sync finished!")

    def stop(self):
        self.stopped = True
        self.eman.stop()

    def login_(self):
        #self.ui.update_events()
        base64string = base64.encodestring("%s:%s" % \
            (self.url.username, self.passwordd))[:-1]
        authheader =  "Basic %s" % base64string
        request = urllib2.Request(self.url)
        request.add_header("AUTHORIZATION", authheader)
        try:
            urllib2.urlopen(request).read()
        except urllib2.URLError, error:
            if hasattr(error, "code"):
                if error.code == 403:
                    raise SyncError(\
                        "Authentification failed: wrong login or password!")
            else:
                raise SyncError(str(error.reason))

    def handshake(self):
        if self.stopped:
            return
        #self.ui.update_events()
        cparams = "<params><client id='%s' name='%s' ver='%s' protocol='%s'" \
            " deck='%s' cardtypes='%s' extra='%s'/></params>\n" % (self.id, \
            self.name, self.version, self.protocol, self.deck, self.cardtypes, \
            self.extra)
        try:
            sparams = urllib2.urlopen(self.url + '/sync/server/params').read()
            response = urllib2.urlopen(PutRequest(\
                self.url + '/sync/client/params', cparams))
            if response.read() != "OK":
                raise SyncError("Handshaking: error on server side.")
        except urllib2.URLError, error:
            raise SyncError("Handshaking: " + str(error))
        else:
            self.eman.set_sync_params(sparams)
            self.eman.update_partnerships_table()

    def set_params(self, params):
        for key in params.keys():
            setattr(self, key, params[key])

    def get_server_media_count(self):
        if self.stopped:
            return
        #self.ui.update_events()
        try:
            return int(urllib2.urlopen(\
                self.url + "/sync/server/history/media/count").read())
        except urllib2.URLError, error:
            raise SyncError("Getting server media count: " + str(error))

    def get_server_history_length(self):
        if self.stopped:
            return
        #self.ui.update_events()
        try:
            return int(urllib2.urlopen(\
                self.url + "/sync/server/history/length").read())
        except urllib2.URLError, error:
            raise SyncError("Getting server history length: " + str(error))

    def get_server_history(self, history_length):
        if self.stopped:
            return
        #self.ui.update_events()
        count = 0
        hsize = float(history_length)
        try:
            #return urllib2.urlopen(self.url + '/sync/server/history')
            response = urllib2.urlopen(self.url + "/sync/server/history")
            response.readline() # get "<history>"
            chunk = response.readline() # get the first item.
            self.ui.show_progressbar()
            while chunk != "</history>\n":
                if self.stopped:
                    return
                self.eman.apply_event(chunk)
                chunk = response.readline()
                count += 1
                self.ui.update_progressbar(count / hsize)
            self.ui.hide_progressbar()
        except urllib2.URLError, error:
            raise SyncError("Getting server history: " + str(error))

    def get_media_history(self):
        #if self.stopped:
        #    return
        #self.ui.update_events()
        try:
            return urllib2.urlopen(self.url + "/sync/server/mediahistory"). \
                readline()
        except urllib2.URLError, error:
            raise SyncError("Getting server media history: " + str(error))
       
    def send_client_history(self, history, history_length):
        #if self.stopped:
        #    return
        #self.update_events()
        #chistory = ''
        #for chunk in history:
        #    chistory += chunk
        #data = str(history_length) + '\n' + chistory + '\n'
        #try:
        #    response = urllib2.urlopen(PutRequest(\
        #        self.url + '/sync/client/history', data))
        #    if response.read() != "OK":
        #        raise SyncError("Sending client history: error on server side.")
        #except urllib2.URLError, error:
        #    raise SyncError("Sending client history: " + str(error))
        import httplib
        conn = httplib.HTTPConnection(url.hostname, url.port)
        conn.putrequest("PUT", "/sync/client/history")
        conn.putheader("User-Agent", "gzip")
        conn.putheader("Accept-Encoding", "gzip")
        conn.putheader("Connection", "keep-alive")
        conn.putheader("Content-Type", "text/plain")
        conn.putheader("Transfer-Encoding", "chunked")
        conn.putheader("Expect", "100-continue")
        conn.putheader("Accept", "*/*")
        conn.endheaders()
       
        count = 0
        hsize = float(history_length + 2)

        # Send client history length.
        conn.send(str(history_length) + "\r\n")
        self.ui.show_progressbar()
        for chunk in history:
            if self.stopped:
                return
            conn.send(chunk + "\r\n")
            count += 1
            self.ui.update_progressbar(count / hsize)

        self.ui.hide_progressbar()
        self.ui.status_bar_message(\
            "Waiting for the server complete. Please wait...")
        response = conn.getresponse()
        #FIXME: analyze response for complete on server side.
        response.read()

    def send_client_media(self, history, media_count):
        #if self.stopped:
        #    return
        count = 0
        hsize = float(media_count)
        self.ui.show_progressbar()
        for child in cElementTree.fromstring(history):
            self.send_media_file(child.find("id").text.split("__for__")[0])
            count += 1
            self.ui.update_progressbar(count / hsize)
        self.ui.hide_progressbar()

    def send_finish_request(self):
        #if self.stopped:
        #    return
        try:
            if urllib2.urlopen(self.url + "/sync/finish").read() != "OK":
                raise SyncError("Finishing sync: error on server side.")
        except urllib2.URLError, error:
            raise SyncError("Finishing syncing: " + str(error))
        else:
            self.eman.update_last_sync_event()

    def get_media_file(self, fname):
        try:
            response = urllib2.urlopen(\
                self.url + "/sync/server/media?fname=%s" % fname)
            data = response.read()
            if data != "CANCEL":
                fobj = open(os.path.join(self.config.mediadir(), fname), "w")
                fobj.write(data)
                fobj.close()
        except urllib2.URLError, error:
            raise SyncError("Getting server media: " + str(error))

    def send_media_file(self, fname):
        mfile = open(os.path.join(self.config.mediadir(), fname), "r")
        data = mfile.read()
        mfile.close()
        try:
            request = PutRequest(self.url + "/sync/client/media?fname=%s" % \
                os.path.basename(fname), data)
            request.add_header("CONTENT_LENGTH", len(data))
            response = urllib2.urlopen(request)
            if response.read() != "OK":
                raise SyncError("Sending client media: error on server side.")
        except urllib2.URLError, error:
            raise SyncError("Sending client media: " + str(error))