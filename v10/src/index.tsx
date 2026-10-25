import React from 'react';
import {registerRoot,Composition} from 'remotion';
import {MagnumV10} from './video';
const Root:React.FC=()=> <Composition id="MagnumV10" component={MagnumV10} durationInFrames={900} fps={30} width={1080} height={1920} defaultProps={{withAudio:false}}/>;
registerRoot(Root);
