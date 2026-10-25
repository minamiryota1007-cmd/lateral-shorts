import React from 'react';
import {registerRoot, Composition} from 'remotion';
import {LateralV7, TOTAL_FRAMES} from './video';
const Root:React.FC=()=> <Composition id="LateralV7" component={LateralV7} durationInFrames={TOTAL_FRAMES} fps={30} width={1080} height={1920}/>;
registerRoot(Root);
