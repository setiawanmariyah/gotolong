
export PROJECT_ROOT=`pwd` 

export PROJ_SOURCE_LOC=$PROJECT_ROOT/src
export PROJ_DATA_LOC=$PROJECT_ROOT/data
export PROJ_REPORTS_LOC=$PROJECT_ROOT/reports
export PROJ_PROFILE=default
export PROJ_PROFILE_DATA_LOC=$PROJECT_ROOT/profile/$PROJ_PROFILE/data
export PROJ_PROFILE_REPORTS_LOC=$PROJECT_ROOT/profile/$PROJ_PROFILE/reports
export PATH=${PATH}:${PROJ_SOURCE_LOC}
export PYTHONPATH=${PYTHONPATH}:${PROJ_SOURCE_LOC}
export QUANDL_KEY=`cat $HOME/quandl.key`
export PLOTLY_API_KEY=`cat $HOME/plotly.key`
