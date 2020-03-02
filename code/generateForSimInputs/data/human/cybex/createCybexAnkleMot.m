%% Cybex experiment human
% Create mot file

dt = 0.02; %seconds
movementFrequency = 1.13;
experimentTime = 120; %seconds
time = 0:dt:experimentTime;
range = 35;
cybexAngle = range*sin(time*2*pi*movementFrequency);
% plot(time,cybexAngle)

pelvis_tilt	= zeros(length(time),1);
pelvis_list = zeros(length(time),1);
pelvis_rotation = zeros(length(time),1);
pelvis_tx = zeros(length(time),1);
pelvis_ty = zeros(length(time),1);
pelvis_tz = zeros(length(time),1);
hip_flexion_r = zeros(length(time),1);
hip_adduction_r = zeros(length(time),1);
hip_rotation_r = zeros(length(time),1);
knee_angle_r = zeros(length(time),1);
ankle_angle_r = cybexAngle';
subtalar_angle_r = zeros(length(time),1);
mtp_angle_r = zeros(length(time),1);
hip_flexion_l = zeros(length(time),1);
hip_adduction_l = zeros(length(time),1);
hip_rotation_l = zeros(length(time),1);
knee_angle_l = zeros(length(time),1);
ankle_angle_l = zeros(length(time),1);
subtalar_angle_l = zeros(length(time),1);
mtp_angle_l = zeros(length(time),1);
lumbar_extension = zeros(length(time),1);
lumbar_bending = zeros(length(time),1);
lumbar_rotation = zeros(length(time),1);

%File creation
outputFileNamePath = 'humanCybexAnkleControl.mot';
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
