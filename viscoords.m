flows = dir('rotsphere3/*flow.npy') ;

figure(400)

clf
ncol = 1 ;
nrow = 3 ;

for n=1:numel(flows)-1
    figure(400)
    clf
    %flo = readNPY(fullfile(flows(n).folder,flows(n).name)) ;
    im1 = imread(fullfile(flows(n).folder,[flows(n).name(1:5) '_im.png'])) ;
    im2 = imread(fullfile(flows(n+1).folder,[flows(n+1).name(1:5) '_im.png'])) ;
    hm1 = imread(fullfile(flows(n).folder,[flows(n).name(1:5) '_imm.png'])) ;
    hm2 = imread(fullfile(flows(n+1).folder,[flows(n+1).name(1:5) '_imm.png'])) ;
    
    im1 = imresize(im1,0.5,'nearest') ;
    im2 = imresize(im2,0.5,'nearest') ;
    hm1 = single(imresize(hm1,0.5,'nearest'))/255 * 2 - 1;
    hm2 = single(imresize(hm2,0.5,'nearest'))/255 * 2 - 1;
    
    %flo = imresize(flo,0.5,'nearest') /.5 ;
    
    mask1 = repmat(im1(:,:,1) == 0 & im1(:,:,2) == 255 & im1(:,:,3) == 0,[1,1,3]) ;
    im1(mask1) = 127 ;
    mask2 = repmat(im2(:,:,1) == 0 & im2(:,:,2) == 255 & im2(:,:,3) == 0,[1,1,3]) ;
    im2(mask2) = 127 ;
    
    hm1(mask1) = 0 ;
    hm2(mask2) = 0 ;
    
    
    im1 = im2single(im1) ;
    im2 = im2single(im2) ;
    
    
    H = floor(size(im1,1)/2) ;
    
    str = 2 ; off = 2 ;
    is = 1:H ;
    is = str .* (is - 1) + off ;
    imsmall = im2(is,is,:) ;
    hm2 = hm2(is,is,:) ;
    
    %im2 = im1; hm2 = hm1 ;
    
    ms = {} ;
    
    subplot(nrow,ncol,1,ms{:}) ;
    %subplot(nrow,ncol,n) ;
    imagesc(im2) ; axis ij ; axis off ;
    
    subplot(nrow,ncol,ncol+1,ms{:})
    %subplot(nrow,ncol,ncol+n)
    hm2vis = makevis(hm2) ;
    imagesc(hm2vis) ; axis ij ; axis off ;
    
    
    % Maps
    subplot(nrow,ncol,2*ncol+1,ms{:})
    %subplot(nrow,ncol,2*ncol+n)
    
    C = reshape(permute(imsmall,[3,1,2]),3,[])' ;
    %bgs = sum(C-.5,2) == 0 ;
    
    hm2_norm = hm2 ./ sqrt(sum(hm2 .^ 2,3)) ;
    x = hm2_norm(:,:,1) ;
    y = hm2_norm(:,:,2) ;
    z = hm2_norm(:,:,3) ;
    
    %scatter(az,el,800,C,'.'); axis off;
    scatter3(x(:),y(:),z(:),800,C,'.'); xlim([-1 1]); ylim([-1 1]);  zlim([-1 1]);
    %print(sprintf('%s/%03d.jpg', out,n), '-djpeg') ;
    drawnow
end

function [hmvis] = makevis(hmin)
hmvis = 0*hmin ;
hmvis = bsxfun(@rdivide, hmin, max(abs(hmin),[],3))/2 + 1/2;
%keyboard

% for h=1:size(hmin,3)
%     hmin = hmin ./ sqrt(sum(hmin .^ 2,3)) ;
%
%     hmin = (hmin + 1)/2 ;
%     hm = hmin(:,:,h) ;
%     %hm = (hm - min(hm(:))) / max(hm(:) - min(hm(:))) ;
%     hmvis(:,:,h) = hm ;
% end
end
