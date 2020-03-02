function CreateMot(fileName,outputFileName,movie)

%%% Kinematic Analysis
% Extract the first 5s
if nargin<1
    fileName='#208_100903_P0_BIP_TM9_4_KIN.csv';
end
if nargin < 2
    outputFileName='Rat208_matlabAll';
end

if nargin<3
    movie=0;
end
    
data = importdata(fileName);

SampleRate = str2double(data.textdata{2,1}(1:6));
Labels = {'R_Iliac_Crest','R_Hip','R_Knee','R_Ankle','R_Toe'};
UsedMarkers = 7:11;
nSamples = 5*SampleRate;
for i = 1:length(Labels)
    eval([Labels{i},' = data.data(:,(UsedMarkers(i)-1)*3-1:1+(UsedMarkers(i)-1)*3);']);
end


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%% Compute angles with no filtering %%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
ToeAnkle = R_Toe-R_Ankle;
KneeAnkle = R_Knee-R_Ankle;

AnkleKnee = R_Ankle-R_Knee;
HipKnee = R_Hip-R_Knee;

CrestHip = R_Iliac_Crest-R_Hip;
KneeHip = R_Knee-R_Hip;

for i=1:length(R_Toe)
    FootAng(i) = 180-atan2d(norm(cross(ToeAnkle(i,:),KneeAnkle(i,:))),dot(ToeAnkle(i,:),KneeAnkle(i,:)));
    LegAng(i) = atan2d(norm(cross(AnkleKnee(i,:),HipKnee(i,:))),dot(AnkleKnee(i,:),HipKnee(i,:)));
    HipAng(i) = atan2d(norm(cross(CrestHip(i,:),KneeHip(i,:))),dot(CrestHip(i,:),KneeHip(i,:)));
end


%%%  Preparare the angles for opensim 
FootAngOS=FootAng-70;
LegAngOS=LegAng-180;
HipAngOS=-(HipAng-90);

figure()
h(1) = subplot(311);
plot(FootAngOS)
set(gca,'xticklabel',0:0.5:5);
ylabel('FootAng')
h(2) = subplot(312);
plot(LegAngOS)
set(gca,'xticklabel',0:0.5:5);
ylabel('LegAng')
h(3) = subplot(313);
plot(HipAngOS)
set(gca,'xticklabel',0:0.5:5);
ylabel('HipAng')
linkaxes(h)
ylim([-120,70])


%%% Compute x and y shifts (in Matlab are y and z)
sacrum_x_value = (R_Iliac_Crest(:,2)-R_Iliac_Crest(1,2))./1000+0.087;
sacrum_y_value = (R_Iliac_Crest(:,3)-R_Iliac_Crest(1,3))./1000+0.063;
   
if movie
    %%% Movie
    figure()
    while 1
        for i=2300:2320
            plot3([R_Ankle(i,1) ,R_Knee(i,1)],[R_Ankle(i,2) R_Knee(i,2)],[R_Ankle(i,3) R_Knee(i,3)],'b')
            hold on
            plot3([R_Ankle(i,1) ,R_Toe(i,1)],[R_Ankle(i,2) R_Toe(i,2)],[R_Ankle(i,3) R_Toe(i,3)],'b')
            plot3([R_Iliac_Crest(i,1) ,R_Hip(i,1)],[R_Iliac_Crest(i,2) R_Hip(i,2)],[R_Iliac_Crest(i,3) R_Hip(i,3)],'b')
            plot3([R_Knee(i,1) ,R_Hip(i,1)],[R_Knee(i,2) R_Hip(i,2)],[R_Knee(i,3) R_Hip(i,3)],'b')
            hold off
            xlim([-50 200])
            ylim([-50 200])
            zlim([-50 200])
            view(-36,30)
            drawnow
            pause(0.12)
            
        end
    end
end

%%% .mot file creation
outputFileNamePath = ['generatedFiles/' outputFileName '_' date '.mot'];
fid = fopen(outputFileNamePath, 'w');	
if fid == -1								
     error(['unable to open ', outputFileNamePath])		
end

totTime = length(FootAng)/SampleRate;


fprintf(fid, ['Coordinates\nversion=1\nnRows=',num2str(length(FootAng)),'\nnColumns=15\ninDegrees=yes\n\n']);
fprintf(fid, 'Units are S.I. units (second, meters, Newtons, ...)\nAngles are in degrees.\n\n');
fprintf(fid, 'endheader\n');
fprintf(fid, 'time\tsacrum_pitch\tsacrum_roll\tsacrum_yaw\tsacrum_x\tsacrum_y\tsacrum_z\tsacroiliac_flx\thip_flx\thip_add\thip_int\tknee_flx\tankle_flx\tankle_add\tankle_int\n');



time = 1;
hip_flx = 9;
knee_flx = 12;
ankle_flx = 13;
sacrum_pitch = 2;
sacrum_y = 6;
sacrum_x = 5;
matrix = zeros(length(FootAngOS),15);
matrix(:,time) = 0.005:0.005:totTime;
matrix(:,hip_flx) = HipAngOS';
matrix(:,knee_flx) = LegAngOS';
matrix(:,ankle_flx) = FootAngOS';
matrix(:,sacrum_pitch) = 30*ones(length(FootAngOS),1);
matrix(:,sacrum_x) = sacrum_x_value;
matrix(:,sacrum_y) = sacrum_y_value;


fprintf(fid,'%4.8f\t%4.8f\t%4.8f\t%4.8f\t%4.8f\t%4.8f\t%4.8f\t%4.8f\t%4.8f\t%4.8f\t%4.8f\t%4.8f\t%4.8f\t%4.8f\t%4.8f\n',matrix');

fclose(fid);