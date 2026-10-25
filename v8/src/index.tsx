import React from 'react';
import {registerRoot,Composition} from 'remotion';
import {Magnum45} from './video';
const Root:React.FC=()=> <Composition id="Magnum45" component={Magnum45} durationInFrames={1350} fps={30} width={1080} height={1920} defaultProps={{withAudio:false}}/>;
registerRoot(Root);
