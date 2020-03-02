function envNorm = computeEnv(signal,emgSamplingRate) 
    n = 5;
    fc = 3;
    wn = fc/(emgSamplingRate/2);
    [b,a] = butter(n,wn,'high');
    env = abs(filtfilt(b, a, signal));
    fc = 10;
    wn = fc/(emgSamplingRate/2);
    [b,a] = butter(n,wn,'low');
    env = filtfilt(b, a, env);
    env(env<0) = 0;
    envNorm = env-min(env);
    envNorm = envNorm./max(envNorm);
    plot(envNorm)
end