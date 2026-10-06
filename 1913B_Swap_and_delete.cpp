#include <bits/stdc++.h>
using namespace std;

int main(){
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);
    long long t;
    cin>>t;
    while(t--){
        string s;
        cin>>s;
        long long count_0=0;
        long long count_1=0;
        for(int i=0;i<s.size();i++){
            if(s[i]=='0'){count_0++;}
            else{count_1++;}
        }
        long long temp=s.size();
        for(int i=0;i<s.size();i++){
            if(s[i]=='0'){if(count_1==0){temp=i;break;}count_1--;}
            else{if(count_0==0){temp=i;break;}count_0--;}
        }
        cout<<s.size()-temp<<endl;
    }
}