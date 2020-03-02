%% Cybex experiment human
% Create mot file

dt = 0.02; %seconds
movementFrequency = 1.13;
experimentTime = 120; %seconds
time = 0:dt:experimentTime;
range = 35;
cybexAngle = range*sin(time*2*pi*movementFrequency);
% plot(time,cybexAngle)

hip_flx = 9;
knee_flx = 12;
ankle_flx = 13;
sacrum_pitch = 2;
sacrum_y = 6;
matrix = zeros(length(time),15);
matrix(:,1) = time;
matrix(:,hip_flx) = 40*ones(length(time),1);
matrix(:,knee_flx) = -120*ones(length(time),1);
matrix(:,ankle_flx) = cybexAngle';
matrix(:,sacrum_pitch) = 30*ones(length(time),1);
matrix(:,sacrum_y) = 0.1*ones(length(time),1);


%%% .mot file creation
outputFileNamePath = 'ratCybexAnkleControl.mot';
fid = fopen(outputFileNamePath, 'w');	
if fid == -1								
     error(['unable to open ', outputFileNamePath])		
end

fprintf(fid, ['Coordinates\nversion=1\nnRows=',num2str(length(time)),'\nnColumns=15\ninDegrees=yes\n\n']);
fprintf(fid, 'Units are S.I. units (second, meters, Newtons, ...)\nAngles are in degrees.\n\n');
fprintf(fid, 'endheader\n');
fprintf(fid, 'time\tsacrum_pitch\tsacrum_roll\tsacrum_yaw\tsacrum_x\tsacrum_y\tsacrum_z\tsacroiliac_flx\thip_flx\thip_add\thip_int\tknee_flx\tankle_flx\tankle_add\tankle_int\n');



fprintf(fid,'%4.8f\t%4.8f\t%4.8f\t%4.8f\t%4.8f\t%4.8f\t%4.8f\t%4.8f\t%4.8f\t%4.8f\t%4.8f\t%4.8f\t%4.8f\t%4.8f\t%4.8f\n',matrix');

fclose(fid);