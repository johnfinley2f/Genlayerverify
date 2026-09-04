const CA="0x0D1A1f2889897cFCb440A194fedaeC131101E0E8";
let conn=false,waddr='',bal=125.4,txrun=false,log=[];
let points=0,txCount=0,walletType='';

const rA=()=>'0x'+Array.from({length:40},()=>'0123456789abcdef'[Math.floor(Math.random()*16)]).join('');
const rH=()=>'0x'+Array.from({length:64},()=>'0123456789abcdef'[Math.floor(Math.random()*16)]).join('');
const sh=a=>a.slice(0,6)+'...'+a.slice(-4);
const slp=ms=>new Promise(r=>setTimeout(r,ms));

function scrollToWallet(){
  document.getElementById('walletPanel').scrollIntoView({behavior:'smooth',block:'center'});
}

/* ===== DUMMY WALLET ===== */
function connectWallet(){
  if(conn)return;
  waddr=rA();conn=true;walletType='dummy';
  onWalletConnected();
  toast('Dummy wallet connected · '+sh(waddr));
}

/* ===== TOAST ===== */
let toastTimer=null;
function toast(msg){
  const t=document.getElementById('toast');
  t.textContent=msg;
  t.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer=setTimeout(()=>t.classList.remove('show'),2600);
}

/* ===== REAL METAMASK CONNECT ===== */
async function connectMetaMask(){
  if(conn)return;

  if(typeof window.ethereum === 'undefined'){
    toast('MetaMask not found — install the extension first');
    return;
  }

  try{
    const accounts=await window.ethereum.request({method:'eth_requestAccounts'});
    if(!accounts || accounts.length===0){
      toast('No account selected in MetaMask');
      return;
    }
    waddr=accounts[0];
    conn=true;
    walletType='metamask';
    onWalletConnected();
    toast('MetaMask connected · '+sh(waddr));
  }catch(err){
    toast('Connection request rejected');
  }
}

/* ===== SHARED CONNECT UI UPDATE ===== */
function onWalletConnected(){
  document.getElementById('wico').classList.add(walletType==='metamask'?'mm':'on');
  const wval=document.getElementById('wval');
  wval.textContent=sh(waddr);
  wval.classList.add(walletType==='metamask'?'mm':'on');

  document.getElementById('balblk').style.display='block';
  document.getElementById('balnum').textContent=bal.toFixed(1);

  document.getElementById('mmbtn').style.display='none';
  document.getElementById('cbtn').style.display='none';
  document.getElementById('dbtn').style.display='block';

  document.getElementById('tbw').textContent=sh(waddr);
  document.getElementById('tbw').classList.add('on');

  document.getElementById('elig').textContent='✓ Eligible';
  document.getElementById('etok').textContent='1 GEN / tx';

  document.getElementById('txfa').textContent=sh(waddr);

  const sbtn=document.getElementById('sbtn');
  sbtn.disabled=false;
  sbtn.textContent='Send 1 GEN';

  document.getElementById('claimStatus').classList.add('ready');
  document.getElementById('claimStatusText').textContent='Ready to claim';
  document.getElementById('claimBtn').disabled=false;
}

/* ===== DISCONNECT ===== */
function disconnectWallet(){
  conn=false;waddr='';walletType='';

  const wico=document.getElementById('wico');
  wico.classList.remove('on','mm');
  const wval=document.getElementById('wval');
  wval.textContent='Not connected';
  wval.classList.remove('on','mm');

  document.getElementById('balblk').style.display='none';
  document.getElementById('mmbtn').style.display='flex';
  document.getElementById('cbtn').style.display='flex';
  document.getElementById('dbtn').style.display='none';

  document.getElementById('tbw').textContent='⬡ Connect Wallet';
  document.getElementById('tbw').classList.remove('on');

  document.getElementById('elig').textContent='— Connect wallet';
  document.getElementById('etok').textContent='—';
  document.getElementById('txfa').textContent='— connect wallet';

  const sbtn=document.getElementById('sbtn');
  sbtn.disabled=true;
  sbtn.textContent='Connect wallet to send';

  document.getElementById('claimStatus').classList.remove('ready');
  document.getElementById('claimStatusText').textContent='Connect wallet to earn points';
  document.getElementById('claimBtn').disabled=true;

  toast('Wallet disconnected');
}

/* ===== SEND 1 GEN (SIMULATED) ===== */
async function sendTx(){
  if(!conn || txrun)return;
  txrun=true;

  const sbtn=document.getElementById('sbtn');
  sbtn.disabled=true;
  document.getElementById('hbox').classList.remove('show');
  document.getElementById('suc').classList.remove('show');
  for(let i=1;i<=4;i++) document.getElementById('s'+i).classList.remove('active','done');
  for(let i=1;i<=5;i++) document.getElementById('v'+i).classList.remove('on');

  document.getElementById('s1').classList.add('active');
  await slp(600);
  document.getElementById('s1').classList.remove('active');
  document.getElementById('s1').classList.add('done');

  document.getElementById('s2').classList.add('active');
  for(let i=1;i<=5;i++){
    await slp(220);
    document.getElementById('v'+i).classList.add('on');
  }
  await slp(300);
  document.getElementById('s2').classList.remove('active');
  document.getElementById('s2').classList.add('done');

  document.getElementById('s3').classList.add('active');
  await slp(600);
  document.getElementById('s3').classList.remove('active');
  document.getElementById('s3').classList.add('done');

  document.getElementById('s4').classList.add('active');
  const hash=rH();
  const block=Math.floor(1000000+Math.random()*900000);
  document.getElementById('hval').textContent=hash;
  document.getElementById('blkn').textContent='#'+block;
  document.getElementById('txst').textContent='Confirmed';
  document.getElementById('hbox').classList.add('show');
  await slp(500);
  document.getElementById('s4').classList.remove('active');
  document.getElementById('s4').classList.add('done');

  bal-=1;
  document.getElementById('balnum').textContent=bal.toFixed(1);

  document.getElementById('suc').classList.add('show');
  sbtn.disabled=false;
  sbtn.textContent='Send 1 GEN';
  txrun=false;
  txCount++;

  log.unshift({hash,block,time:'just now'});
  renderHistory();

  points+=10;
  updatePoints();

  toast('Transaction confirmed · '+sh(hash));
}

/* ===== HISTORY RENDER ===== */
function renderHistory(){
  const wrap=document.getElementById('hrows');
  if(log.length===0){
    wrap.innerHTML='<div class="empty">No transactions yet — connect wallet and send 1 GEN to start.</div>';
    return;
  }
  wrap.innerHTML=log.slice(0,8).map(tx=>`
    <div class="hrow">
      <div>
        <div class="hrhash">${sh(tx.hash)}</div>
        <div class="hrblk">Block #${tx.block}</div>
      </div>
      <div style="text-align:right">
        <div class="hramt">1 GEN</div>
        <div class="hrtim">${tx.time}</div>
      </div>
    </div>
  `).join('');
}

/* ===== POINTS ===== */
function updatePoints(){
  document.getElementById('ptsnum').textContent=points;
  const pct=Math.min(100,Math.round((points/100)*100));
  document.getElementById('ptspct').textContent=pct+'%';
  document.getElementById('ptsbar').style.width=pct+'%';
}

function claimPoints(){
  if(!conn)return;
  points+=25;
  updatePoints();
  toast('+25 points claimed');
}

/* ===== COPY CONTRACT ADDRESS ===== */
function copyContract(){
  navigator.clipboard.writeText(CA).then(()=>{
    toast('Contract address copied');
  });
}
