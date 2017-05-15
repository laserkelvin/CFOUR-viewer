#/bin/bash
# ----------- Parameters --------- #
#$ -S /bin/bash
#$ -l mres=5G,h_data=5G,h_vmem=5G
#$ -cwd
#$ -q uThC.q -l lopri
#$ -j y
#$ -N calc{0}
#
# -------- User Variables -------- #
scrtop={1}
scrdir=$scrtop/$JOB_ID
outputdir={2}
cfourdir={3}
export PATH=$cfourdir:$PATH
# ----------- Modules ------------ #
#
module load intel
#
# ------------- Job -------------- #
#
export OMP_NUM_THREADS=1
mkdir $scrdir
cp ZMAT $scrdir
cp ZMAT $outputdir
echo `date` job $JOB_NAME started in $QUEUE with jobID=$JOB_ID on $HOSTNAME
echo {0} > $scrdir/calc{0}
cd $scrdir
xcfour > $outputdir/$JOB_NAME.log
echo `date` calculation finished.
echo Space used `du -sh`
cp FCM* $outputdir/
cp JOB* $outputdir/
cp JAIN* $outputdir/
cp ZMATnew $outputdir/
cp ZMATtemp $outputdir/
cp *.o* $outputdir/
xja2fja                       # For finite differences calculations
cp FJOBARC $outputdir/
xclean
rm -r $scrdir
parseCFOUR {0}                # Generate a report for the calculation
