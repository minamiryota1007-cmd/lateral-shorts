import React from 'react';
import {registerRoot,Composition} from 'remotion';
import {MagnumV9} from './video';
const Root:React.FC=()=> <Composition id="MagnumV9" component={MagnumV9} durationInFrames={1350} fps={30} width={1080} height={1920} defaultProps={{withAudio:false}}/>;
registerRoot(Root);
