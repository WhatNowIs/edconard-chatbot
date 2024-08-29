(self.webpackChunk_N_E=self.webpackChunk_N_E||[]).push([[392],{74081:function(){},1696:function(){},62811:function(){},65665:function(){},68665:function(){},70483:function(e,a,s){"use strict";s.d(a,{default:function(){return eB}});var t,l,n,r,i,o,d=s(57437),c=s(24266),u=s(2265),m=s(71538),h=s(12218),p=s(44839),x=s(96164);function f(){for(var e=arguments.length,a=Array(e),s=0;s<e;s++)a[s]=arguments[s];return(0,x.m6)((0,p.W)(a))}let g=(0,h.j)("inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",{variants:{variant:{default:"bg-primary text-primary-foreground hover:bg-primary/90",destructive:"bg-destructive text-destructive-foreground hover:bg-destructive/90",outline:"border border-input bg-background hover:bg-accent hover:text-accent-foreground",secondary:"bg-secondary text-secondary-foreground hover:bg-secondary/80",ghost:"hover:bg-accent hover:text-accent-foreground",link:"text-primary underline-offset-4 hover:underline"},size:{default:"h-10 px-4 py-2",sm:"h-9 rounded-md px-3",lg:"h-11 rounded-md px-8",icon:"h-10 w-10"}},defaultVariants:{variant:"default",size:"default"}}),j=u.forwardRef((e,a)=>{let{className:s,variant:t,size:l,asChild:n=!1,...r}=e,i=n?m.g7:"button";return(0,d.jsx)(i,{className:f(g({variant:t,size:l,className:s})),ref:a,...r})});j.displayName="Button";var v=s(74109),b=s(42365);function w(e){var a;let{config:s,onFileUpload:t,onFileError:l}=e,[n,r]=(0,u.useState)(!1),i=(null==s?void 0:s.inputId)||"fileInput",o=(null==s?void 0:s.fileSizeLimit)||52428800,c=null==s?void 0:s.allowedExtensions,m=null!==(a=null==s?void 0:s.checkExtension)&&void 0!==a?a:e=>c&&!c.includes(e)?"Invalid file type. Please select a file with one of these formats: ".concat(c.join(",")):null,h=e=>e.size>o,p=()=>{document.getElementById(i).value=""},x=async e=>{var a;let s=null===(a=e.target.files)||void 0===a?void 0:a[0];s&&(r(!0),await j(s),p(),r(!1))},j=async e=>{let a=l||window.alert,s=m(e.name.split(".").pop()||"");return s?a(s):h(e)?a("File size exceeded. Limit is ".concat(o/1024/1024," MB")):void await t(e)};return(0,d.jsxs)("div",{className:"self-stretch",children:[(0,d.jsx)("input",{type:"file",id:i,style:{display:"none"},onChange:x,accept:null==c?void 0:c.join(","),disabled:(null==s?void 0:s.disabled)||n}),(0,d.jsx)("label",{htmlFor:i,className:f(g({variant:"secondary",size:"icon"}),"cursor-pointer",n&&"opacity-50"),children:n?(0,d.jsx)(v.Z,{className:"h-4 w-4 animate-spin"}):(0,d.jsx)(b.Z,{className:"-rotate-45 w-4 h-4"})})]})}let N=u.forwardRef((e,a)=>{let{className:s,type:t,...l}=e;return(0,d.jsx)("input",{type:t,className:f("flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50",s),ref:a,...l})});N.displayName="Input";var y=s(59738),C=s(66648);function D(e){let{url:a,onRemove:s}=e;return(0,d.jsxs)("div",{className:"relative w-20 h-20 group",children:[(0,d.jsx)(C.default,{src:a,alt:"Uploaded image",fill:!0,className:"object-cover w-full h-full rounded-xl hover:brightness-75"}),(0,d.jsx)("div",{className:f("absolute -top-2 -right-2 w-6 h-6 z-10 bg-gray-500 text-white rounded-full hidden group-hover:block"),children:(0,d.jsx)(y.Z,{className:"w-6 h-6 bg-gray-500 text-white rounded-full",onClick:s})})]})}function k(e){let[a,s]=(0,u.useState)(null),t=async e=>{s(await new Promise((a,s)=>{let t=new FileReader;t.readAsDataURL(e),t.onload=()=>a(t.result),t.onerror=e=>s(e)}))},l=async a=>{var s,l;try{if(e.multiModal&&a.type.startsWith("image/"))return await t(a);null===(s=e.onFileUpload)||void 0===s||s.call(e,a)}catch(a){null===(l=e.onFileError)||void 0===l||l.call(e,a.message)}};return(0,d.jsxs)("form",{onSubmit:t=>{if(a){e.handleSubmit(t,{data:{imageUrl:a}}),s(null);return}e.handleSubmit(t)},className:"rounded-xl bg-white p-4 shadow-xl space-y-4",children:[a&&(0,d.jsx)(D,{url:a,onRemove:()=>s(null)}),(0,d.jsxs)("div",{className:"flex w-full items-start justify-between gap-4 ",children:[(0,d.jsx)(N,{autoFocus:!0,name:"message",placeholder:"Type a message",className:"flex-1",value:e.input,onChange:e.handleInputChange}),(0,d.jsx)(w,{onFileUpload:l,onFileError:e.onFileError}),(0,d.jsx)(j,{type:"submit",disabled:e.isLoading,children:"Send message"})]})]})}var F=s(70459),S=s(66706);function R(e){return(0,d.jsxs)("div",{className:"space-x-4",children:[e.showStop&&(0,d.jsxs)(j,{variant:"outline",size:"sm",onClick:e.stop,children:[(0,d.jsx)(F.Z,{className:"mr-2 h-4 w-4"}),"Stop generating"]}),e.showReload&&(0,d.jsxs)(j,{variant:"outline",size:"sm",onClick:e.reload,children:[(0,d.jsx)(S.Z,{className:"mr-2 h-4 w-4"}),"Regenerate"]})]})}var z=s(22468),_=s(6884),L=s(71145),E=s(40475);function T(e){let{role:a}=e;return"user"===a?(0,d.jsx)("div",{className:"flex h-8 w-8 shrink-0 select-none items-center justify-center rounded-md border bg-background shadow",children:(0,d.jsx)(L.Z,{className:"h-4 w-4"})}):(0,d.jsx)("div",{className:"flex h-8 w-8 shrink-0 select-none items-center justify-center rounded-md border bg-black text-white shadow",children:(0,d.jsx)(E.Z,{className:"h-4 w-4"})})}var I=s(42421),U=s(87592),Z=s(40882);let P=Z.fC,O=Z.wy,B=Z.Fw,M=(0,u.createContext)(void 0),A=()=>{let e=(0,u.useContext)(M);if(void 0===e)throw Error("usePDF must be used within a PDFProvider");return e};(t=r||(r={})).purple="llama-purple",t.magenta="llama-magenta",t.red="llama-red",t.orange="llama-orange",t.yellow="llama-yellow",t.lime="llama-lime",t.teal="llama-teal",t.cyan="llama-cyan",t.blue="llama-blue",t.indigo="llama-indigo";let H={"llama-purple":"border-llama-purple","llama-magenta":"border-llama-magenta","llama-red":"border-llama-red","llama-indigo":"border-llama-indigo","llama-lime":"border-llama-lime","llama-orange":"border-llama-orange","llama-blue":"border-llama-blue","llama-yellow":"border-llama-yellow","llama-teal":"border-llama-teal","llama-cyan":"border-llama-cyan"};var $=e=>{let{citation:a}=e,{setPdfFocusState:s}=A(),t=(e,t)=>{s({documentId:e,pageNumber:t,citation:a})};return(0,d.jsxs)("div",{className:"mx-1.5 mb-2 min-h-[25px] min-w-[160px] cursor-pointer rounded border-l-8 bg-gray-00 p-1 hover:bg-gray-15  ".concat(H[a.color]),onClick:()=>t(a.documentId,a.pageNumber),children:[(0,d.jsxs)("div",{className:"flex items-center",children:[(0,d.jsxs)("div",{className:"mr-1 text-xs font-bold text-black",children:[a.ticker," "]}),(0,d.jsxs)("div",{className:"text-[10px]",children:["p. ",a.pageNumber]})]}),(0,d.jsx)("p",{className:"line-clamp-2 text-[10px] font-light leading-3",children:a.snippet})]})};function V(e){let{data:a}=e;return(0,d.jsx)("div",{className:" mr-2 flex w-full overflow-x-scroll pl-2 ",children:null==a?void 0:a.map((e,a)=>{if(e.metadata){var s,t;return(0,d.jsx)($,{citation:{documentId:e.id,snippet:e.text,pageNumber:null===(s=e.metadata)||void 0===s?void 0:s.page_label,ticker:null===(t=e.metadata)||void 0===t?void 0:t.file_name,color:H["llama-lime"]}},"".concat(e.id,"-").concat(a))}})})}function W(e){let{data:a,citations:s,isLoading:t}=e,[l,n]=(0,u.useState)(!1),r=l?(0,d.jsx)(I.Z,{className:"h-4 w-4"}):(0,d.jsx)(U.Z,{className:"h-4 w-4"});return(0,d.jsx)("div",{className:"border-l-2 border-indigo-400 pl-2",children:(0,d.jsxs)(P,{open:l,onOpenChange:n,children:[(0,d.jsx)(O,{asChild:!0,children:(0,d.jsxs)(j,{variant:"secondary",className:"space-x-2",children:[t?(0,d.jsx)(v.Z,{className:"h-4 w-4 animate-spin"}):null,(0,d.jsx)("span",{children:l?"Hide events":"Show events"}),r]})}),(0,d.jsxs)(B,{asChild:!0,children:[(0,d.jsx)("div",{className:"mt-4 text-sm space-y-2",children:a.map((e,a)=>(0,d.jsx)("div",{children:e.title},a))}),(0,d.jsx)(V,{data:s})]})]})})}function J(e){let{data:a}=e;return(0,d.jsx)("div",{className:"rounded-md max-w-[200px] shadow-md",children:(0,d.jsx)(C.default,{src:a.url,width:0,height:0,sizes:"100vw",style:{width:"100%",height:"auto"},alt:""})})}var X=s(93080);let Y=X.fC,G=X.xz,K=u.forwardRef((e,a)=>{let{className:s,align:t="center",sideOffset:l=4,...n}=e;return(0,d.jsx)(X.VY,{ref:a,align:t,sideOffset:l,className:f("z-50 w-64 rounded-md border bg-popover p-4 text-popover-foreground shadow-md outline-none data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[side=bottom]:slide-in-from-top-2 data-[side=left]:slide-in-from-right-2 data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2",s),...n})});K.displayName=X.VY.displayName;var q=s(20357);let Q=e=>{let a=!!q.env.NEXT_PUBLIC_CHAT_API,s="/api/".concat("data","/").concat(e);if(a){let e=new URL(q.env.NEXT_PUBLIC_CHAT_API).origin;return"".concat(e,"/").concat(s)}return s};function ee(e){let{timeout:a=2e3}=e,[s,t]=u.useState(!1);return{isCopied:s,copyToClipboard:e=>{var s;(null===(s=navigator.clipboard)||void 0===s?void 0:s.writeText)&&e&&navigator.clipboard.writeText(e).then(()=>{t(!0),setTimeout(()=>{t(!1)},a)})}}}var ea=s(93241),es=s(3),et=s(63957);let el=e=>{let{shouldScaleBackground:a=!0,...s}=e;return(0,d.jsx)(et.d.Root,{shouldScaleBackground:a,...s})};el.displayName="Drawer";let en=et.d.Trigger,er=et.d.Portal,ei=et.d.Close,eo=u.forwardRef((e,a)=>{let{className:s,...t}=e;return(0,d.jsx)(et.d.Overlay,{ref:a,className:f("fixed inset-0 z-50 bg-black/80",s),...t})});eo.displayName=et.d.Overlay.displayName;let ed=u.forwardRef((e,a)=>{let{className:s,children:t,...l}=e;return(0,d.jsxs)(er,{children:[(0,d.jsx)(eo,{}),(0,d.jsxs)(et.d.Content,{ref:a,className:f("fixed inset-x-0 bottom-0 z-50 mt-24 flex h-auto flex-col rounded-t-[10px] border bg-background",s),...l,children:[(0,d.jsx)("div",{className:"mx-auto mt-4 h-2 w-[100px] rounded-full bg-muted"}),t]})]})});ed.displayName="DrawerContent";let ec=e=>{let{className:a,...s}=e;return(0,d.jsx)("div",{className:f("grid gap-1.5 p-4 text-center sm:text-left",a),...s})};ec.displayName="DrawerHeader";let eu=u.forwardRef((e,a)=>{let{className:s,...t}=e;return(0,d.jsx)(et.d.Title,{ref:a,className:f("text-lg font-semibold leading-none tracking-tight",s),...t})});eu.displayName=et.d.Title.displayName;let em=u.forwardRef((e,a)=>{let{className:s,...t}=e;return(0,d.jsx)(et.d.Description,{ref:a,className:f("text-sm text-muted-foreground",s),...t})});function eh(e){return(0,d.jsxs)(el,{direction:"left",children:[(0,d.jsx)(en,{children:e.trigger}),(0,d.jsxs)(ed,{className:"w-3/5 mt-24 h-full max-h-[96%] ",children:[(0,d.jsxs)(ec,{className:"flex justify-between",children:[(0,d.jsxs)("div",{className:"space-y-2",children:[(0,d.jsx)(eu,{children:"PDF Content Modified"}),(0,d.jsxs)(em,{children:["File path:"," ",(0,d.jsx)("a",{className:"hover:text-blue-900",href:e.url,target:"_blank",children:e.path})]})]}),(0,d.jsx)(ei,{asChild:!0,children:(0,d.jsx)(j,{variant:"outline",children:"Close"})})]}),(0,d.jsx)("div",{className:"m-4",children:(0,d.jsx)(ea.Z,{children:(0,d.jsx)(es.Z,{file:{id:e.documentId,url:e.url}})})})]})]})}function ep(e){let{index:a}=e;return(0,d.jsx)("div",{className:"text-xs w-5 h-5 rounded-full bg-gray-100 mb-2 flex items-center justify-center hover:text-white hover:bg-primary hover:cursor-pointer",children:a+1})}function ex(e){let{data:a}=e,s=(0,u.useMemo)(()=>{let e={};return a.nodes.filter(e=>{var a;return(null!==(a=e.score)&&void 0!==a?a:1)>.3}).sort((e,a)=>{var s,t;return(null!==(s=a.score)&&void 0!==s?s:1)-(null!==(t=e.score)&&void 0!==t?t:1)}).forEach(a=>{var s;let t=function(e){var a,s,t;if("string"==typeof e.metadata.URL){let a=e.metadata.URL;return{id:e.id,type:0,path:a,url:a,text:e.text,page_number:null===(s=e.metadata)||void 0===s?void 0:s.page_label}}if("string"==typeof e.metadata.file_path){let a=e.metadata.file_name;return{id:e.id,type:1,path:e.metadata.file_path,url:Q(a),text:e.text,page_number:null===(t=e.metadata)||void 0===t?void 0:t.page_label}}return{id:e.id,type:2,text:e.text,page_number:null===(a=e.metadata)||void 0===a?void 0:a.page_label}}(a),l=null!==(s=t.path)&&void 0!==s?s:t.id;e[l]||(e[l]=t)}),Object.values(e)},[a.nodes]);return 0===s.length?null:(0,d.jsxs)("div",{className:"space-x-2 text-sm",children:[(0,d.jsx)("span",{className:"font-semibold",children:"Sources:"}),(0,d.jsx)("div",{className:"inline-flex gap-1 items-center",children:s.map((e,a)=>{var s;return(null===(s=e.path)||void 0===s?void 0:s.endsWith(".pdf"))?(0,d.jsx)(eh,{documentId:e.id,url:e.url,path:e.path,trigger:(0,d.jsx)(ep,{index:a})},e.id):(0,d.jsx)("div",{children:(0,d.jsxs)(Y,{children:[(0,d.jsx)(G,{children:(0,d.jsx)(ep,{index:a})}),(0,d.jsx)(K,{className:"w-[320px]",children:(0,d.jsx)(ef,{nodeInfo:e})})]})},e.id)})})]})}function ef(e){let{nodeInfo:a}=e,{setPdfFocusState:s}=A(),t=(e,a,t)=>{s({documentId:e,pageNumber:a,citation:t})},{isCopied:l,copyToClipboard:n}=ee({timeout:1e3});return 2!==a.type?(0,d.jsxs)("div",{className:"flex items-center my-2",children:[(0,d.jsx)("a",{className:"hover:text-blue-900",href:a.url,target:"_blank",children:(0,d.jsx)("span",{children:a.path})}),(0,d.jsx)(j,{onClick:()=>{n(a.path),t(a.id,a.page_number,{documentId:a.id,snippet:a.text,pageNumber:a.page_number,color:r.teal,ticker:""})},size:"icon",variant:"ghost",className:"h-12 w-12 shrink-0",children:l?(0,d.jsx)(z.Z,{className:"h-4 w-4"}):(0,d.jsx)(_.Z,{className:"h-4 w-4"})})]}):(0,d.jsx)("p",{children:"Sorry, unknown node type. Please add a new renderer in the NodeInfo component."})}em.displayName=et.d.Description.displayName,(l=i||(i={}))[l.URL=0]="URL",l[l.FILE=1]="FILE",l[l.UNKNOWN=2]="UNKNOWN";let eg={0:{icon:(0,d.jsx)("span",{children:"☀️"}),status:"Clear sky"},1:{icon:(0,d.jsx)("span",{children:"\uD83C\uDF24️"}),status:"Mainly clear"},2:{icon:(0,d.jsx)("span",{children:"☁️"}),status:"Partly cloudy"},3:{icon:(0,d.jsx)("span",{children:"☁️"}),status:"Overcast"},45:{icon:(0,d.jsx)("span",{children:"\uD83C\uDF2B️"}),status:"Fog"},48:{icon:(0,d.jsx)("span",{children:"\uD83C\uDF2B️"}),status:"Depositing rime fog"},51:{icon:(0,d.jsx)("span",{children:"\uD83C\uDF27️"}),status:"Drizzle"},53:{icon:(0,d.jsx)("span",{children:"\uD83C\uDF27️"}),status:"Drizzle"},55:{icon:(0,d.jsx)("span",{children:"\uD83C\uDF27️"}),status:"Drizzle"},56:{icon:(0,d.jsx)("span",{children:"\uD83C\uDF27️"}),status:"Freezing Drizzle"},57:{icon:(0,d.jsx)("span",{children:"\uD83C\uDF27️"}),status:"Freezing Drizzle"},61:{icon:(0,d.jsx)("span",{children:"\uD83C\uDF27️"}),status:"Rain"},63:{icon:(0,d.jsx)("span",{children:"\uD83C\uDF27️"}),status:"Rain"},65:{icon:(0,d.jsx)("span",{children:"\uD83C\uDF27️"}),status:"Rain"},66:{icon:(0,d.jsx)("span",{children:"\uD83C\uDF27️"}),status:"Freezing Rain"},67:{icon:(0,d.jsx)("span",{children:"\uD83C\uDF27️"}),status:"Freezing Rain"},71:{icon:(0,d.jsx)("span",{children:"❄️"}),status:"Snow fall"},73:{icon:(0,d.jsx)("span",{children:"❄️"}),status:"Snow fall"},75:{icon:(0,d.jsx)("span",{children:"❄️"}),status:"Snow fall"},77:{icon:(0,d.jsx)("span",{children:"❄️"}),status:"Snow grains"},80:{icon:(0,d.jsx)("span",{children:"\uD83C\uDF27️"}),status:"Rain showers"},81:{icon:(0,d.jsx)("span",{children:"\uD83C\uDF27️"}),status:"Rain showers"},82:{icon:(0,d.jsx)("span",{children:"\uD83C\uDF27️"}),status:"Rain showers"},85:{icon:(0,d.jsx)("span",{children:"❄️"}),status:"Snow showers"},86:{icon:(0,d.jsx)("span",{children:"❄️"}),status:"Snow showers"},95:{icon:(0,d.jsx)("span",{children:"⛈️"}),status:"Thunderstorm"},96:{icon:(0,d.jsx)("span",{children:"⛈️"}),status:"Thunderstorm"},99:{icon:(0,d.jsx)("span",{children:"⛈️"}),status:"Thunderstorm"}},ej=e=>new Date(e).toLocaleDateString("en-US",{weekday:"long"});function ev(e){let{data:a}=e,s=new Date(a.current.time).toLocaleDateString("en-US",{weekday:"long",month:"long",day:"numeric"});return(0,d.jsxs)("div",{className:"bg-[#61B9F2] rounded-2xl shadow-xl p-5 space-y-4 text-white w-fit",children:[(0,d.jsxs)("div",{className:"flex justify-between",children:[(0,d.jsxs)("div",{className:"space-y-2",children:[(0,d.jsx)("div",{className:"text-xl",children:s}),(0,d.jsxs)("div",{className:"text-5xl font-semibold flex gap-4",children:[(0,d.jsxs)("span",{children:[a.current.temperature_2m," ",a.current_units.temperature_2m]}),eg[a.current.weather_code].icon]})]}),(0,d.jsx)("span",{className:"text-xl",children:eg[a.current.weather_code].status})]}),(0,d.jsx)("div",{className:"gap-2 grid grid-cols-6",children:a.daily.time.map((e,s)=>0===s?null:(0,d.jsxs)("div",{className:"flex flex-col items-center gap-4",children:[(0,d.jsx)("span",{children:ej(e)}),(0,d.jsx)("div",{className:"text-4xl",children:eg[a.daily.weather_code[s]].icon}),(0,d.jsx)("span",{className:"text-sm",children:eg[a.daily.weather_code[s]].status})]},e))})]})}function eb(e){let{data:a}=e;if(!a)return null;let{toolCall:s,toolOutput:t}=a;if(t.isError)return(0,d.jsxs)("div",{className:"border-l-2 border-red-400 pl-2",children:["There was an error when calling the tool ",s.name," with input:"," ",(0,d.jsx)("br",{}),JSON.stringify(s.input)]});if("get_weather_information"===s.name){let e=t.output;return(0,d.jsx)(ev,{data:e})}return null}s(7395);var ew=s(53150),eN=s(60724),ey=s(57439),eC=s(93676),eD=s(37164),ek=s(28040),eF=s(38666);let eS=ek.Z,eR={javascript:".js",python:".py",java:".java",c:".c",cpp:".cpp","c++":".cpp","c#":".cs",ruby:".rb",php:".php",swift:".swift","objective-c":".m",kotlin:".kt",typescript:".ts",go:".go",perl:".pl",rust:".rs",scala:".scala",haskell:".hs",lua:".lua",shell:".sh",sql:".sql",html:".html",css:".css"},ez=function(e){let a=arguments.length>1&&void 0!==arguments[1]&&arguments[1],s="ABCDEFGHJKLMNPQRSTUVWXY3456789",t="";for(let a=0;a<e;a++)t+=s.charAt(Math.floor(Math.random()*s.length));return a?t.toLowerCase():t},e_=(0,u.memo)(e=>{let{language:a,value:s}=e,{isCopied:t,copyToClipboard:l}=ee({timeout:2e3});return(0,d.jsxs)("div",{className:"codeblock relative w-full bg-zinc-950 font-sans",children:[(0,d.jsxs)("div",{className:"flex w-full items-center justify-between bg-zinc-800 px-6 py-2 pr-4 text-zinc-100",children:[(0,d.jsx)("span",{className:"text-xs lowercase",children:a}),(0,d.jsxs)("div",{className:"flex items-center space-x-1",children:[(0,d.jsxs)(j,{variant:"ghost",onClick:()=>{let e=eR[a]||".file",t="file-".concat(ez(3,!0)).concat(e),l=window.prompt("Enter file name",t);if(!l)return;let n=new Blob([s],{type:"text/plain"}),r=URL.createObjectURL(n),i=document.createElement("a");i.download=l,i.href=r,i.style.display="none",document.body.appendChild(i),i.click(),document.body.removeChild(i),URL.revokeObjectURL(r)},size:"icon",children:[(0,d.jsx)(eD.Z,{}),(0,d.jsx)("span",{className:"sr-only",children:"Download"})]}),(0,d.jsxs)(j,{variant:"ghost",size:"icon",onClick:()=>{t||l(s)},children:[t?(0,d.jsx)(z.Z,{className:"h-4 w-4"}):(0,d.jsx)(_.Z,{className:"h-4 w-4"}),(0,d.jsx)("span",{className:"sr-only",children:"Copy code"})]})]})]}),(0,d.jsx)(eS,{language:a,style:eF.RY,PreTag:"div",showLineNumbers:!0,customStyle:{width:"100%",background:"transparent",padding:"1.5rem 1rem",borderRadius:"0.5rem"},codeTagProps:{style:{fontSize:"0.9rem",fontFamily:"var(--font-mono)"}},children:s})]})});e_.displayName="CodeBlock";let eL=(0,u.memo)(ew.D,(e,a)=>e.children===a.children&&e.className===a.className),eE=e=>e.replace(RegExp("\\\\\\[(.*?)\\\\\\]","gs"),(e,a)=>"$$".concat(a,"$$")).replace(RegExp("\\\\\\((.*?)\\\\\\)","gs"),(e,a)=>"$".concat(a,"$"));function eT(e){let{content:a}=e,s=eE(a);return(0,d.jsx)(eL,{className:"prose dark:prose-invert prose-p:leading-relaxed prose-pre:p-0 break-words custom-markdown",remarkPlugins:[ey.Z,eC.Z],rehypePlugins:[eN.Z],components:{p(e){let{children:a}=e;return(0,d.jsx)("p",{className:"mb-2 last:mb-0",children:a})},code(e){let{node:a,inline:s,className:t,children:l,...n}=e;if(l.length){if("▍"==l[0])return(0,d.jsx)("span",{className:"mt-1 animate-pulse cursor-default",children:"▍"});l[0]=l[0].replace("`▍`","▍")}let r=/language-(\w+)/.exec(t||"");return s?(0,d.jsx)("code",{className:t,...n,children:l}):(0,d.jsx)(e_,{language:r&&r[1]||"",value:String(l).replace(/\n$/,""),...n},Math.random())}},children:s})}function eI(e,a){return e.filter(e=>e.type===a).map(e=>e.data)}function eU(e){let{message:a,isLoading:s}=e,t=a.annotations;if(!(null==t?void 0:t.length))return(0,d.jsx)(eT,{content:a.content});let l=eI(t,o.IMAGE),n=eI(t,o.EVENTS),r=eI(t,o.SOURCES),i=eI(t,o.TOOLS),c=[{order:-3,component:l[0]?(0,d.jsx)(J,{data:l[0]}):null},{order:-2,component:n.length>0?(0,d.jsx)(W,{isLoading:s,data:n,citations:r[0].nodes}):null},{order:-1,component:i[0]?(0,d.jsx)(eb,{data:i[0]}):null},{order:0,component:(0,d.jsx)(eT,{content:a.content})},{order:1,component:r[0]?(0,d.jsx)(ex,{data:r[0]}):null}];return(0,d.jsx)("div",{className:"flex-1 gap-4 flex flex-col",children:c.sort((e,a)=>e.order-a.order).map((e,a)=>(0,d.jsx)(u.Fragment,{children:e.component},a))})}function eZ(e){let{chatMessage:a,isLoading:s}=e,{isCopied:t,copyToClipboard:l}=ee({timeout:2e3});return(0,d.jsxs)("div",{className:"flex items-start gap-4 pr-5 pt-5",children:[(0,d.jsx)(T,{role:a.role}),(0,d.jsxs)("div",{className:"group flex flex-1 justify-between gap-2",children:[(0,d.jsx)(eU,{message:a,isLoading:s}),(0,d.jsx)(j,{onClick:()=>l(a.content),size:"icon",variant:"ghost",className:"h-8 w-8 opacity-0 group-hover:opacity-100",children:t?(0,d.jsx)(z.Z,{className:"h-4 w-4"}):(0,d.jsx)(_.Z,{className:"h-4 w-4"})})]})]})}function eP(e){let a=(0,u.useRef)(null),s=e.messages.length,t=e.messages[s-1],l=()=>{a.current&&(a.current.scrollTop=a.current.scrollHeight)},n=s>0&&(null==t?void 0:t.role)!=="user",r=e.reload&&!e.isLoading&&n,i=e.stop&&e.isLoading,o=e.isLoading&&!n;return(0,u.useEffect)(()=>{l()},[s,t]),(0,d.jsxs)("div",{className:"w-full h-full rounded-xl bg-white p-4 shadow-xl border overflow-auto",children:[(0,d.jsxs)("div",{className:"flex flex-col gap-5 divide-y pb-4",ref:a,children:[e.messages.map(a=>(0,d.jsx)(eZ,{chatMessage:a,isLoading:e.isLoading},a.id)),o&&(0,d.jsx)("div",{className:"flex justify-center items-center pt-10",children:(0,d.jsx)(v.Z,{className:"h-4 w-4 animate-spin"})})]}),(0,d.jsx)("div",{className:"flex justify-end py-4",children:(0,d.jsx)(R,{reload:e.reload,stop:e.stop,showReload:r,showStop:i})})]})}(n=o||(o={})).IMAGE="image",n.SOURCES="sources",n.EVENTS="events",n.TOOLS="tools";var eO=s(20357);function eB(e){let{layout:a}=e,{messages:s,input:t,isLoading:l,handleSubmit:n,handleInputChange:r,reload:i,stop:o}=(0,c.RJ)({api:eO.env.NEXT_PUBLIC_CHAT_API,headers:{"Content-Type":"application/json"},onError:e=>{alert(JSON.parse(e.message).detail)}});return(0,d.jsxs)("div",{className:"flex flex-col space-y-4 justify-between w-full pb-4 ".concat("fit"===a?"h-full p-2":"max-w-5xl h-[50vh]"),children:[(0,d.jsx)(eP,{messages:s,isLoading:l,reload:i,stop:o}),(0,d.jsx)(k,{input:t,handleSubmit:n,handleInputChange:r,isLoading:l,multiModal:!0})]})}}}]);