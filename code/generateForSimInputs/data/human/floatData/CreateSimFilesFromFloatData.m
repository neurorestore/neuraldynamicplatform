function CreateSimFilesFromFloatData()


%% Load c3d files
acq = btkReadAcquisition('H_JBM_20150109_04TM_NF_01.c3d');
md = btkGetMetaData(acq);

markers = btkGetMarkers(acq);
angles = btkGetAngles(acq);
analogs = btkGetAnalogs(acq);

emgSamplingRate = 1000;
kinSamplingRate = 100;


%% Create mot file

time= 0:(1 / kinSamplingRate):((md.children.POINT.children.FRAMES.info.values - 1) / kinSamplingRate);
pelvis_tilt	= 4.84455933*ones(length(time),1);
pelvis_list = -1.84559258*ones(length(time),1);
pelvis_rotation = -0.77772078*ones(length(time),1);
pelvis_tx = 0.60102028*ones(length(time),1);
pelvis_ty = 1.04559875*ones(length(time),1);
pelvis_tz = -0.02160049*ones(length(time),1);

hip_flexion_r = angles.RHipAngles(:,1);
hip_flexion_r = lowPass(6,hip_flexion_r ,kinSamplingRate);

hip_adduction_r = -2.90617367*ones(length(time),1);
hip_rotation_r = -6.95037445*ones(length(time),1);


knee_angle_r = -angles.RKneeAngles(:,1);
knee_angle_r = lowPass(6,knee_angle_r ,kinSamplingRate);

ankle_angle_r = angles.RAnkleAngles(:,1);
ankle_angle_r = lowPass(6,ankle_angle_r ,kinSamplingRate);

subtalar_angle_r = -0.00000082*ones(length(time),1);
mtp_angle_r = 0.00000000*ones(length(time),1);

hip_flexion_l = angles.LHipAngles(:,1);
hip_flexion_l = lowPass(6,hip_flexion_l ,kinSamplingRate);


hip_adduction_l = 1.38076320*ones(length(time),1);
hip_rotation_l = 0.20135362*ones(length(time),1);

knee_angle_l = -angles.LKneeAngles(:,1);
knee_angle_l = lowPass(6,knee_angle_l ,kinSamplingRate);

ankle_angle_l = angles.LAnkleAngles(:,1);
ankle_angle_l = lowPass(6,ankle_angle_l ,kinSamplingRate);

subtalar_angle_l = 0.00000249*ones(length(time),1);
mtp_angle_l = 0.00000000*ones(length(time),1);

lumbar_extension = -19.54310531*ones(length(time),1);
lumbar_bending = -0.47001089*ones(length(time),1);
lumbar_rotation = -4.72635202*ones(length(time),1);


figure()
subplot(311)
plot(hip_flexion_r)
subplot(312)
plot(knee_angle_r)
subplot(313)
plot(ankle_angle_r)

%File creation
outputFileNamePath = ['generatedFiles/H_JBM_20150109_04TM_NF_01_',date,'.mot'];
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

%% Create kin file with toe y kin 

leftHeel = markers.LHEE(:,3);
rightHeel = markers.RHEE(:,3);
leftToe = markers.LTOE(:,3);
rightToe = markers.RTOE(:,3);


%File creation
outputFileNamePath = ['generatedFiles/H_JBM_20150109_04TM_NF_01_',date,'_KIN.csv'];
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
matrix(:,4) = leftHeel;
matrix(:,5) = rightHeel;

fprintf(fid,'%4.8f\t%4.8f\t%4.8f\t%4.8f\t%4.8f\n',matrix');
fclose(fid);


%% Create muscle activity file with left and rigt sol,ta and gl

time= 0:(1 / emgSamplingRate):((length(analogs.Fx1) - 1) / emgSamplingRate);


TA_L = computeEnv(analogs.LTA,emgSamplingRate);
TA_R = computeEnv(analogs.RTA,emgSamplingRate);
SOL_L = computeEnv(analogs.LSol,emgSamplingRate);
SOL_R = computeEnv(analogs.RSol,emgSamplingRate);
GL_L = computeEnv(analogs.LLG,emgSamplingRate);
GL_R = computeEnv(analogs.RLG,emgSamplingRate);




%File creation
outputFileNamePath = ['generatedFiles/H_JBM_20150109_04TM_NF_01_',date,'_EMG.csv'];
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
