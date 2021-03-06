
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "Lib_SetOfFrictionLaws.h"


void LinearIncreaseFunction(double Y[], double y_o, double x, double x1, double x2, double Amplitude)
{
    Y[0] = x*Amplitude + y_o;
}

void ExponentialIncreaseFunction(double Y[], double y_o, double x, double x1, double x2, double Amplitude)
{
    if (x > x1 && x < x2)
    {
        Y[0] = pow(x,2.0)*Amplitude/1000.0 + y_o;
    } else {
        Y[0] = y_o;
    }
}


void RectFunction(double Y[], double y_o, double x, double x1, double x2, double Amplitude)
{
    if (x > x1 && x < x2)
    {
        Y[0] = y_o + Amplitude;
    } else {
        Y[0] = y_o;
    }
}

void SawFunction(double Y[], double y_o, double x, double x1, double x2, double Amplitude)
{
    if (x > x1 && x < x2)
    {
        Y[0] = y_o + x*Amplitude/1000.0;
    } else {
        Y[0] = y_o;
    }
}



void PrescribedFunction(double Y[], double y_o, double x, double x1, double x2, double Amplitude)
{
    void (*PresFunArray[])(double*,double, double, double,double,double) =\
    {LinearIncreaseFunction, ExponentialIncreaseFunction,RectFunction,SawFunction};
    
    int FuncNo = 3;

    if (FuncNo > 3) exit(1);
    
    (*PresFunArray[FuncNo])(Y, y_o, x, x1, x2, Amplitude);
}


int main(int nargs,char *args[])
{
    FILE *fp;
    double Tau[1000], Slip[1000], SlipRate[1000], Fric[1000],time[1000];
    double mu_s = 0.6, mu_d = 0.3, D_c = 0.01;
    double sigma_n[3];
    int i;
    double ThetaDot;

    double DeltaTime = 0.01;
    double DeltaSlip = 0.0002;
     
    // ListOfParameters = [a, b, mu_o, V_o, D_c]
    double ListOfParameters[5] = {0.011, 0.016, 0.2, 1.0 * pow(10.0,-1.0), D_c};
    
    double Theta, theta_oo, theta_o;
    
    theta_o = D_c / (ListOfParameters[3]);
    
    sigma_n[0] = -10, sigma_n[1] = -5, sigma_n[2] = -2;
    Slip[0] = 0.001;
    SlipRate[0] = ListOfParameters[3];
    time[0] = 0.0;

    { // LSW Test
        fp = fopen("./Output/TestLSW.txt","w+");
        printf("--> LSW Test\n");

        for (i=1; i<1000; i++)
        {   
            Slip[i] = Slip[i-1] + SlipRate[0]*DeltaTime;
            time[i] = DeltaTime + time[i-1];
            SlipRate[i] = (Slip[i] - Slip[i-1])/DeltaTime;

            FricSW(&Fric[i], mu_s, mu_d, D_c, &Slip[i]);
            EvalSlipWeakening(&Tau[i],sigma_n, mu_s, mu_d, D_c, &Slip[i]);
            fprintf(fp, "%f ; %f ; %f ; %f ; %f ; %f \n", time[i], Tau[i], Slip[i], SlipRate[i], Fric[i], theta_o);
        }
        fclose(fp);
    }
    

    theta_oo=theta_o;
    { // RS Test
        fp = fopen("./Output/TestRS_HealingLaw_NoThetaUp.txt","w+");
        printf("--> LRS Test\n");

        for (i=1; i<1000; i++)
        {
            PrescribedFunction(&SlipRate[i], ListOfParameters[3], i, 200, 600, 0.002);
            Slip[i] = Slip[i-1] + SlipRate[i-1]*DeltaTime;
            

            State_AgingLaw(theta_o, SlipRate[i] , ListOfParameters, DeltaTime, &Theta);
            theta_o = Theta;
            
            FricRS(&Fric[i], SlipRate[i], Theta, ListOfParameters);
            EvalRateStateFriction(&Tau[i], sigma_n, SlipRate[i], Theta, ListOfParameters);
            fprintf(fp, "%f ; %f ; %f ; %f ; %f ; %f \n", time[i], Tau[i], Slip[i], SlipRate[i], Fric[i], theta_o);
        }
        fclose(fp);
    }
    theta_o=theta_oo;
    { // ModRS Test
        fp = fopen("./Output/TestModRS_HealingLaw.txt","w+");
        printf("--> ModRS Test\n");
        for (i=1; i<1000; i++)
        {

            State_AgingLaw(theta_o, SlipRate[i] , ListOfParameters, DeltaTime, &Theta);
            theta_o = Theta;
            
            FricModRS(&Fric[i], SlipRate[i], Theta, ListOfParameters);
            EvalModRateStateFriction(&Tau[i], sigma_n, SlipRate[i], Theta, ListOfParameters);
            fprintf(fp, "%f ; %f ; %f ; %f ; %f ; %f \n", time[i], Tau[i], Slip[i], SlipRate[i], Fric[i], theta_o);
        }
        fclose(fp);
    }

    theta_o=theta_oo;
    { // SR Updating Theta Test - Healing Law
        fp = fopen("./Output/TestRS_HealingLaw.txt","w+");
        printf("--> RS-Healing Law Test\n");
        for (i=1; i<1000; i++)
        {
            PrescribedFunction(&SlipRate[i], ListOfParameters[3], i, 200, 600, 0.002);
            Slip[i] = Slip[i-1] + SlipRate[i-1]*DeltaTime;
            
            
            DotState_AgingLaw( ListOfParameters, SlipRate[i], theta_o, &ThetaDot);
            theta_o = theta_o + ThetaDot*DeltaTime;

            FricRS(&Fric[i], SlipRate[i], theta_o, ListOfParameters);
            EvalRateStateFriction(&Tau[i], sigma_n, SlipRate[i], theta_o, ListOfParameters);
            fprintf(fp, "%f ; %f ; %f ; %f ; %f ; %f \n", time[i], Tau[i], Slip[i], SlipRate[i], Fric[i], theta_o);
        }
        fclose(fp);
    }

    theta_o=theta_oo;
    { // SR Updating Theta Test - Slip Law
        fp = fopen("./Output/TestRS_SlipLaw.txt","w+");
        printf("--> RS-Slip Law Test\n");
        for (i=1; i<1000; i++)
        {
            PrescribedFunction(&SlipRate[i], ListOfParameters[3], i, 200, 600, 0.002);
            Slip[i] = Slip[i-1] + SlipRate[i-1]*DeltaTime;
            

            DotState_SlipLaw( ListOfParameters, SlipRate[i], theta_o, &ThetaDot);
            theta_o = theta_o + ThetaDot*DeltaTime;
            
            FricRS(&Fric[i], SlipRate[i], theta_o, ListOfParameters);
            EvalRateStateFriction(&Tau[i], sigma_n, SlipRate[i], theta_o, ListOfParameters);
            fprintf(fp, "%f ; %f ; %f ; %f ; %f ; %f \n", time[i], Tau[i], Slip[i], SlipRate[i], Fric[i], theta_o);
        }
        fclose(fp);
    }
    theta_o=theta_oo*2;
    { // SR Updating Theta Test - PRZ Law
        fp = fopen("./Output/TestRS_PRZLaw.txt","w+");
        printf("--> RS-PRZ Law Test\n");
        for (i=1; i<1000; i++)
        {
            PrescribedFunction(&SlipRate[i], ListOfParameters[3], i, 200, 600, 0.002);
            Slip[i] = Slip[i-1] + SlipRate[i-1]*DeltaTime;


            DotState_PerrinRiceZhengLaw( ListOfParameters, SlipRate[i], theta_o, &ThetaDot);
            theta_o = theta_o + ThetaDot*DeltaTime;
            
            FricRS(&Fric[i], SlipRate[i], theta_o, ListOfParameters);
            EvalRateStateFriction(&Tau[i], sigma_n, SlipRate[i], theta_o, ListOfParameters);
            fprintf(fp, "%f ; %f ; %f ; %f ; %f ; %f \n", time[i], Tau[i], Slip[i], SlipRate[i], Fric[i], theta_o);
        }
        fclose(fp);
    }
  
    return(0);
}
