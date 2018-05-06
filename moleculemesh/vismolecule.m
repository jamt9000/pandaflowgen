addpath(genpath('/Users/jamesthewlis/Code/gptoolbox'),':');
addpath('/Users/jamesthewlis/Code/iso2mesh')

[V,F] = readOBJ('clathrin.obj') ;
[V,F] = clean(V,F) ;
[V,F] = meshcheckrepair(V,F,'meshfix') ;

[F,V] = reducepatch(F,V,0.01) ;


V = 0.1*V;
trimesh(F,V(:,1),V(:,2),V(:,3));

writeOBJ('clathrinfix.obj', V,F) ;

mkdir('smoothed')
conn = meshconn(F,size(V,1)) ;
for its=1:1:20
    Vs = smoothsurf(V, [], conn, its, rand, 'lowpass') ;
    writeOBJ(sprintf('smoothed/clathrinfixsmth%02d.obj',its), Vs,F) ;
    figure(2)
    trimesh(F,Vs(:,1),Vs(:,2),Vs(:,3));
    drawnow
    pause(0.5)
end

