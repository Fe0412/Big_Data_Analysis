x=[0 1 2 3 4 5];
y=[0 20 60 68 77 110];
coef=polyfit(x,y,1); % coef ????????????
a0=coef(1); a1=coef(2);
ybest=a0*x+a1; % ?????????????
sum_sq=sum((y-ybest).^2); % ??????? 356.82
axis([-1,6,-20,120])
plot(x,ybest,x,y,'o'), title('Linear regression estimate'), grid