node default{

  include apt
  exec { 'apt-upgrade':
    command   => '/usr/bin/apt-get --quiet --yes --fix-broken upgrade',
    logoutput => 'on_failure',
    path      => '/usr/bin:/usr/sbin:/bin:/usr/local/bin:/usr/local/sbin:/sbin',
  }

  include git
  include gcc
  include cmake
  include unzip

  class { 'python' :
    version    => 'system',
    pip        => 'present',
    dev        => 'present',
    virtualenv => 'present',
  }

  $packages = [
    'python-imaging',
    'libjpeg8',
    'libjpeg62-dev',
    'libfreetype6',
    'libfreetype6-dev',
  ]

  package { $packages:
    ensure  => latest,
    require => Class[ 'python' ],
  }

  include opencv

}
