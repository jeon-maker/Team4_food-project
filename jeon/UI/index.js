/**
 * @format
 */

import {AppRegistry} from 'react-native';
import App from './App';
import App2 from './App2';
import Read from './Read';
import {name as appName} from './app.json';
import Todos from './root/Todos';

AppRegistry.registerComponent(appName, () => App2);
