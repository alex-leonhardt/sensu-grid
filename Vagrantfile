# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure(2) do |config|
  config.vm.box = "centos65-x86_64-20140116"
  config.vm.provider "virtualbox" do |vb|
    vb.memory = "768"
  end

  config.vm.network "forwarded_port", guest: 3000, host: 3000
  config.vm.network "forwarded_port", guest: 4567, host: 4567
  #config.vm.network "forwarded_port", guest: 5000, host: 5000

  config.vm.synced_folder ".", "/vagrant"
  config.vm.synced_folder ".", "/opt/sensu-grid"

  config.vm.provision "shell", inline: <<-SHELL
    sudo yum -y install epel-release vim-enhanced
    sudo su -c cat >/etc/yum.repos.d/sensu.repo<<EOF
[sensu]
name=sensu-main
baseurl=http://repos.sensuapp.org/yum/el/6/x86_64/
gpgcheck=0
enabled=1
EOF
  sudo yum -y install sensu uchiwa rabbitmq-server redis

  sudo chkconfig rabbitmq-server on
  sudo chkconfig redis on
  sudo chkconfig sensu-client on
  sudo chkconfig sensu-server on
  sudo chkconfig sensu-api on
  sudo chkconfig uchiwa on

  cp -rp /vagrant/vagrant-sensu-config/* /etc/sensu/

  sudo service rabbitmq-server restart
  sudo service redis restart
  sudo service sensu-client stop
  sudo service sensu-client start
  sudo service sensu-api stop
  sudo service sensu-api start
  sudo service sensu-server stop
  sudo service sensu-server start
  sudo service uchiwa restart

  sudo yum -y install supervisor python-pip python-devel
  sudo pip install -r /vagrant/requirements.txt

  sudo cp /vagrant/start-scripts/supervisord.conf /etc/supervisord.conf
  sudo service supervisord start

  SHELL
end
