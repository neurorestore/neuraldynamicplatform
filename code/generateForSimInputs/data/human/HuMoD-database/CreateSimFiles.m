function CreateSimFiles(subject,speed)

%% Load straight walking dataset
if nargin<1
    subject = 'A';
    speed = '1.3';
end
data = load([subject,'/',speed,'.mat']);
startTime = 40;
endTime = 50;

%% Create mot file

startIndex = round(startTime *data.motion.frameRate);
endIndex = round(endTime *data.motion.frameRate);

indexHJ_R = find(strcmp(data.motion.trajectoryLabels, 'rHJZ_R'));
indexKJ_R = find(strcmp(data.motion.trajectoryLabels, 'rKJZ_R'));
indexAJ_R = find(strcmp(data.motion.trajectoryLabels, 'rAJZ_R'));
indexHJ_L = find(strcmp(data.motion.trajectoryLabels, 'rHJZ_L'));
indexKJ_L = find(strcmp(data.motion.trajectoryLabels, 'rKJZ_L'));
indexAJ_L = find(strcmp(data.motion.trajectoryLabels, 'rAJZ_L'));

time= 0:(1 / data.motion.frameRate):((data.motion.frames - 1) / data.motion.frameRate);
time = time(startIndex:endIndex);
pelvis_tilt	= 4.84455933*ones(length(time),1);
pelvis_list = -1.84559258*ones(length(time),1);
pelvis_rotation = -0.77772078*ones(length(time),1);
pelvis_tx = 0.60102028*ones(length(time),1);
pelvis_ty = 1.04559875*ones(length(time),1);
pelvis_tz = -0.02160049*ones(length(time),1);
hip_flexion_r = rad2deg(data.motion.trajectory.q(indexHJ_R, startIndex:endIndex))';
hip_adduction_r = -2.90617367*ones(length(time),1);
hip_rotation_r = -6.95037445*ones(length(time),1);
knee_angle_r = rad2deg(data.motion.trajectory.q(indexKJ_R, startIndex:endIndex))';
ankle_angle_r = rad2deg(data.motion.trajectory.q(indexAJ_R, startIndex:endIndex))';
subtalar_angle_r = -0.00000082*ones(length(time),1);
mtp_angle_r = 0.00000000*ones(length(time),1);
hip_flexion_l = rad2deg(data.motion.trajectory.q(indexHJ_L, startIndex:endIndex))';
hip_adduction_l = 1.38076320*ones(length(time),1);
hip_rotation_l = 0.20135362*ones(length(time),1);
knee_angle_l = rad2deg(data.motion.trajectory.q(indexKJ_L, startIndex:endIndex))';
ankle_angle_l = rad2deg(data.motion.trajectory.q(indexAJ_L, startIndex:endIndex))';
subtalar_angle_l = 0.00000249*ones(length(time),1);
mtp_angle_l = 0.00000000*ones(length(time),1);
lumbar_extension = -19.54310531*ones(length(time),1);
lumbar_bending = -0.47001089*ones(length(time),1);
lumbar_rotation = -4.72635202*ones(length(time),1);

%File creation
outputFileNamePath = ['generatedFiles/Subject_',subject,'_speed_',speed,'_',date,'.mot'];
fid = fopen(outputFileNamePath, 'w');	
if fid == -1								
     error(['unable to open ', outputFileNamePath])		
end

fprintf(fid, ['Coordinates\nversion=1\nnRows=',num2str(length(time)),'\nnColumns=24\ninDegrees=yes\n\n']);
fprintf(fid, 'Units are S.I. units (second, meters, Newtons, ...)\nAngles are in degrees.\n\n');
fprintf(fid, 'endheader\n');
fprintf(fid, 'time\tpelvis_tilt\tpelvis_list\tpelvis_rotation\tpelvis_tx\tpelvis_ty\tpelvis_tz\thip_flexion_r\thip_adduction_r\thip_rotation_r\tknee_angle_r\tankle_angle_r\tsubtalar_angle_r\tmtp_angle_r\thip_flexion_l\thip_adduction_l\thip_rotation_l\tknee_angle_l\tankle_angle_l\tsubtalar_angle_l\tmtp_angle_l\tlumbar_extension\tlumbar_bending\tlumbar_rotation\n');

matrix = zeros(length(time),24);
matrix(:,1) = time;
matrix(:,2) = pelvis_tilt;
matrix(:,3) = pelvis_list;
matrix(:,4) = pelvis_rotation;
matrix(:,5) = pelvis_tx;
matrix(:,6) = pelvis_ty;
matrix(:,7) = pelvis_tz;
matrix(:,8) = hip_flexion_r;
matrix(:,9) = hip_adduction_r;
matrix(:,10) = hip_rotation_r;
matrix(:,11) = knee_angle_r;
matrix(:,12) = ankle_angle_r;
matrix(:,13) = subtalar_angle_r;
matrix(:,14) = mtp_angle_r;
matrix(:,15) = hip_flexion_l;
matrix(:,16) = hip_adduction_l;
matrix(:,17) = hip_rotation_l;
matrix(:,18) = knee_angle_l;
matrix(:,19) = ankle_angle_l;
matrix(:,20) = subtalar_angle_l;
matrix(:,21) = mtp_angle_l;
matrix(:,22) = lumbar_extension;
matrix(:,23) = lumbar_bending;
matrix(:,24) = lumbar_rotation;

fprintf(fid,'%4.8f\t%4.8f\t%4.8f\t%4.8f\t%4.8f\t%4.8f\t%4.8f\t%4.8f\t%4.8f\t%4.8f\t%4.8f\t%4.8f\t%4.8f\t%4.8f\t%4.8f\t%4.8f\t%4.8f\t%4.8f\t%4.8f\t%4.8f\t%4.8f\t%4.8f\t%4.8f\t%4.8f\n',matrix');
fclose(fid);

%% Create kin file with toe and calf y kin 

indexC_L = find(strcmp(data.motion.markerLabels, 'CAL_L'));
leftCalf = data.motion.markerY(indexC_L , startIndex:endIndex)';
indexC_R = find(strcmp(data.motion.markerLabels, 'CAL_R'));
rightCalf = data.motion.markerY(indexC_R , startIndex:endIndex)';

indexAJ_L = find(strcmp(data.motion.markerLabels, 'MT5_L'));
indexAJ_R = find(strcmp(data.motion.markerLabels, 'MT5_R'));
leftToe = data.motion.markerY(indexAJ_L , startIndex:endIndex)';
rightToe = data.motion.markerY(indexAJ_R , startIndex:endIndex)';

%File creation
outputFileNamePath = ['generatedFiles/Subject_',subject,'_speed_',speed,'_',date,'_KIN.csv'];
fid = fopen(outputFileNamePath, 'w');	
if fid == -1								
     error(['unable to open ', outputFileNamePath])		
end

fprintf(fid, 'Toe y trajetcories');
fprintf(fid, 'endheader\n\n');
fprintf(fid, 'time\tleftToe\trightToe\tleftCalf\trightCalf\n');

matrix = zeros(length(time),5);
matrix(:,1) = time;
matrix(:,2) = leftToe;
matrix(:,3) = rightToe;
matrix(:,4) = leftCalf;
matrix(:,5) = rightCalf;

fprintf(fid,'%4.8f\t%4.8f\t%4.8f\t%4.8f\t%4.8f\n',matrix');
fclose(fid);


%% Create muscle activity file with left and rigt sol,ta and gl

startIndex = round(startTime *data.muscle.frameRate);
endIndex = round(endTime *data.muscle.frameRate);

time= 0:(1 / data.muscle.frameRate):((data.muscle.frames - 1) / data.muscle.frameRate);
time = time(startIndex:endIndex);



indexTA_L = find(strcmp(data.muscle.muscleLabels, 'TIA_L'));
indexTA_R = find(strcmp(data.muscle.muscleLabels, 'TIA_R'));
indexSOL_L = find(strcmp(data.muscle.muscleLabels, 'SOL_L'));
indexSOL_R = find(strcmp(data.muscle.muscleLabels, 'SOL_R'));
indexGL_L = find(strcmp(data.muscle.muscleLabels, 'GSL_L'));
indexGL_R = find(strcmp(data.muscle.muscleLabels, 'GSL_R'));

TA_L = data.muscle.activities.filtered(indexTA_L , startIndex:endIndex)';
TA_R = data.muscle.activities.filtered(indexTA_R , startIndex:endIndex)';
SOL_L = data.muscle.activities.filtered(indexSOL_L , startIndex:endIndex)';
SOL_R = data.muscle.activities.filtered(indexSOL_R , startIndex:endIndex)';
GL_L = data.muscle.activities.filtered(indexGL_L , startIndex:endIndex)';
GL_R = data.muscle.activities.filtered(indexGL_R , startIndex:endIndex)';



%File creation
outputFileNamePath = ['generatedFiles/Subject_',subject,'_speed_',speed,'_',date,'_EMG.csv'];
fid = fopen(outputFileNamePath, 'w');	
if fid == -1								
     error(['unable to open ', outputFileNamePath])		
end

fprintf(fid, 'Filtered (MAV) muscles activity');
fprintf(fid, 'endheader\n\n');
fprintf(fid, 'time\tSOL_L\tSOL_R\tTA_L\tTA_R\tGL_L\tGL_R\n');

matrix = zeros(length(time),7);
matrix(:,1) = time;
matrix(:,2) = SOL_L;
matrix(:,3) = SOL_R;
matrix(:,4) = TA_L;
matrix(:,5) = TA_R;
matrix(:,6) = GL_L;
matrix(:,7) = GL_R;

fprintf(fid,'%4.8f\t%4.8f\t%4.8f\t%4.8f\t%4.8f\t%4.8f\t%4.8f\n',matrix');
fclose(fid);

