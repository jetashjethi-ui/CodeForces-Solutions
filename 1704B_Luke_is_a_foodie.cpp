#include <bits/stdc++.h>
using namespace std;

int main(){
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);
    long long t;
    cin>>t;
    while(t--){
        long long n,x;
        cin>>n>>x;
        long long arr[n];
        for(long long i=0;i<n;i++){
            cin>>arr[i];
        }
        long long R=arr[0]+x,L=arr[0]-x;
        long long ans=0;
        for(long long i=1;i<n;i++){
            L=max(L,arr[i]-x);
            R=min(R,arr[i]+x);
            if(L>R){
                ans++;
                L=arr[i]-x;
                R=arr[i]+x;
            }
        }
        cout<<ans<<endl;
    }
}