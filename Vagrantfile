# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure(2) do |config|

config.vm.provision "shell", inline: <<-SHELL
    sudo yum -y install epel-release vim-enhanced
    sudo su -c cat >/etc/yum.repos.d/sensu.repo<<EOF
[sensu]
name=sensu
baseurl=http://sensu.global.ssl.fastly.net/yum/\\$basearch/
gpgcheck=0
enabled=1
EOF
    sudo yum -y install sensu uchiwa rabbitmq-server redis
    sudo rabbitmq-plugins enable rabbitmq_management
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
    sudo service sensu-api stop
    sudo service sensu-api start
    sudo service sensu-server stop
    sudo service sensu-server start
    sudo service uchiwa restart
    sudo service sensu-client start

    # create sensu-grid user
    sudo useradd -c "sensu-grid user" -d /opt/sensu-grid -M -s /sbin/nologin -r sensu-grid

    sudo yum -y install supervisor python-pip python-devel python-virtualenv
    sudo pip install --upgrade pip ||:
    sudo pip install -r /vagrant/requirements.txt ||:
    sudo touch /var/log/sensu-grid.log && sudo chown sensu-grid: /var/log/sensu-grid.log

    sudo cp /vagrant/start-scripts/supervisord.conf /etc/supervisord.conf
    sudo service supervisord start

    SHELL

    config.vm.define "vagrant1" do |vagrant1|

        vagrant1.vm.box = "bento/centos-7.2"
        vagrant1.vm.provider "virtualbox" do |vb|
            vb.memory = "768"
        end

        vagrant1.vm.network "forwarded_port", guest: 3000, host: 3000
        vagrant1.vm.network "forwarded_port", guest: 4567, host: 4567
        vagrant1.vm.network "forwarded_port", guest: 5000, host: 5000
        vagrant1.vm.network "forwarded_port", guest: 15672, host: 15672

        vagrant1.vm.synced_folder ".", "/vagrant"
        vagrant1.vm.synced_folder ".", "/opt/sensu-grid"


    end

    config.vm.define "vagrant2" do |vagrant2|


        vagrant2.vm.box = "bento/centos-6.7"
        vagrant2.vm.provider "virtualbox" do |vb|
            vb.memory = "768"
        end

        vagrant2.vm.network "forwarded_port", guest: 3000, host: 3001
        vagrant2.vm.network "forwarded_port", guest: 4567, host: 4568

        vagrant2.vm.synced_folder ".", "/vagrant"
        vagrant2.vm.synced_folder ".", "/opt/sensu-grid"


    end

    config.vm.define "vagrant3" do |vagrant3|


        vagrant3.vm.box = "bento/centos-6.7"
        vagrant3.vm.provider "virtualbox" do |vb|
            vb.memory = "768"
        end

        vagrant3.vm.network "forwarded_port", guest: 3000, host: 3002
        vagrant3.vm.network "forwarded_port", guest: 4567, host: 4569

        vagrant3.vm.synced_folder ".", "/vagrant"
        vagrant3.vm.synced_folder ".", "/opt/sensu-grid"


    end



end
