ssh web01.gamejam 'rm -rf /tmp/galax; mkdir /tmp/galax'
ssh web02.gamejam 'rm -rf /tmp/galax; mkdir /tmp/galax'

scp -r * web01.gamejam:/tmp/galax/
scp -r * web02.gamejam:/tmp/galax/

ssh web01.gamejam 'sudo cp -vr /tmp/galax/* /opt/iggj-eventpage/flamejam/static/galax/'
ssh web02.gamejam 'sudo cp -vr /tmp/galax/* /opt/iggj-eventpage/flamejam/static/galax/'
