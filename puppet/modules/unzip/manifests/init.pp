class unzip{

  $packages = [
    'unzip',
  ]

  package { $packages: ensure => latest }

}
