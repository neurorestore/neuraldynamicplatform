function filtSig = lowPass(fc,signal,samplingRate) 
    n = 5;
    wn = fc/(samplingRate/2);
    [b,a] = butter(n,wn,'low');
    filtSig = filtfilt(b, a, signal);
    
    plot(signal)
    hold on 
    plot(filtSig)
    hold off
end