from conans import ConanFile, CMake, tools, AutoToolsBuildEnvironment
import os

class WebrtcaudioprocessingConan(ConanFile):
    name = "webrtc-audio-processing"
    version = "0.2"
    description = "This is meant to be a more Linux packaging friendly copy of the AudioProcessing module from the WebRTC project"
    url = "https://github.com/conan-multimedia/webrtc-audio-processing"
    homepage = "https://freedesktop.org/software/pulseaudio/webrtc-audio-processing/"
    license = "BSD_like"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=True"
    generators = "cmake"
    source_subfolder = "source_subfolder"

    def source(self):
        tarball_name = '{name}-{version}.tar'.format(name=self.name, version=self.version)
        archive_name = '%s.xz' % tarball_name
        #'http://freedesktop.org/software/pulseaudio/webrtc-audio-processing/{0}-{1}.tar.xz'.format(name, version)
        url_ = 'http://172.16.64.65:8081/artifactory/gstreamer/{0}'.format(archive_name)
        tools.download(url_, archive_name)

        if self.settings.os == 'Windows':
            self.run('7z x %s' % archive_name)
            self.run('7z x %s' % tarball_name)
            os.unlink(tarball_name)
        else:
            self.run('tar -xJf %s' % archive_name)
        os.rename('%s-%s'%(self.name,self.version) , self.source_subfolder)
        os.unlink(archive_name)

    def build(self):
        with tools.chdir(self.source_subfolder):
            self.run("autoreconf -f -i")

            autotools = AutoToolsBuildEnvironment(self)
            _args = ["--prefix=%s/builddir"%(os.getcwd()), "--enable-introspection"]
            if self.options.shared:
                _args.extend(['--enable-shared=yes','--enable-static=no'])
            else:
                _args.extend(['--enable-shared=no','--enable-static=yes'])
            autotools.configure(args=_args)
            autotools.make(args=["-j4"])
            autotools.install()

    def package(self):
        if tools.os_info.is_linux:
            with tools.chdir(self.source_subfolder):
                self.copy("*", src="%s/builddir"%(os.getcwd()))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

