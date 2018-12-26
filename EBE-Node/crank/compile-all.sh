#! /usr/bin/env bash
(cd ..
for ii in superMC VISHNew photonEmission iSS iS osc2u urqmd fs
    do
    (cd $ii; make; make clean)
done

# let's build MUSIC which needs MPI support
(cd music-hydro; mkdir build; cd build; cmake ".."; make; make install; make clean; cd ..; rm -rf build)

echo "Compiling finished."
echo "Next generate jobs using generate-jobs-XXX.sh."
)
