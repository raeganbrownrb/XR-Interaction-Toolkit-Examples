import torch
import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

from utils import Config

class LSTMCSVDataset(torch.utils.data.Dataset):
    def __init__(self, root_path, output_type=Config['data_type'], look_back=10, step_value = 1):
        files = os.listdir(root_path)
        files = [f for f in files if f.endswith('.csv')]
        all_data=[]

        for file in files:
            csv_data = pd.read_csv(os.path.join(root_path,file)).iloc[:,1:41]

            csv_data['relativeHandRPosx'] = csv_data.headPosx-csv_data.handRPosx
            csv_data['relativeHandRPosy'] = csv_data['headPosy']-csv_data['handRPosy']
            csv_data['relativeHandRPosz'] = csv_data['headPosz']-csv_data['handRPosz']
            csv_data['relativeHandLPosx'] = csv_data['headPosx']-csv_data['handLPosx']
            csv_data['relativeHandLPosy'] = csv_data['headPosy']-csv_data['handLPosy']
            csv_data['relativeHandLPosz'] = csv_data['headPosz']-csv_data['handLPosz']
            csv_data['relativeTracker1Posx'] = csv_data['headPosx']-csv_data['tracker1Posx']
            csv_data['relativeTracker1Posy'] = csv_data['headPosy']-csv_data['tracker1Posy']
            csv_data['relativeTracker1Posz'] = csv_data['headPosz']-csv_data['tracker1Posz']

            data = np.array([csv_data])
            all_data.append(data)
        self.data = np.concatenate(all_data, axis=1).squeeze(0)
        self.scaler = MinMaxScaler(feature_range=(-1,1))
        self.scaler.fit(self.data)
        self.scaled_data = self.scaler.transform(self.data)
        self.lstm_data = []
        for i in range(len(self.scaled_data)-look_back-1):
            a = self.scaled_data[i:(i+look_back):step_value]
            self.lstm_data.append(a)
        self.lstm_data = np.array(self.lstm_data)
        self.output_type = output_type
        self.look_back = look_back
        self.step_value = step_value
    def __len__(self):
        return self.lstm_data.shape[0]

    def __getitem__(self, idx):
        row = self.lstm_data[idx]
        headPosx = row[:, 0]
        headPosy = row[:,1]
        headPosz = row[:,2]
        headRotx = row[:,3]
        headRoty = row[:,4]
        headRotz = row[:,5]
        headRotQx = row[:,6]
        headRotQy = row[:,7]
        headRotQz = row[:,8]
        headRotQw = row[:,9]

        handRPosx = row[:,10]
        handRPosy = row[:,11]
        handRPosz = row[:,12]
        handRRotx = row[:,13]
        handRRoty = row[:,14]
        handRRotz = row[:,15]
        handRRotQx = row[:,16]
        handRRotQy = row[:,17]
        handRRotQz = row[:,18]
        handRRotQw = row[:,19]

        handLPosx = row[:,20]
        handLPosy = row[:,21]
        handLPosz = row[:,22]
        handLRotx = row[:,23]
        handLRoty = row[:,24]
        handLRotz = row[:,25]
        handLRotQx = row[:,26]
        handLRotQy = row[:,27]
        handLRotQz = row[:,28]
        handLRotQw = row[:,29]

        tracker1Posx = row[:,30]
        tracker1Posy = row[:,31]
        tracker1Posz = row[:,32]
        tracker1Rotx = row[:,33]
        tracker1Roty = row[:,34]
        tracker1Rotz = row[:,35]
        tracker1RotQx = row[:,36]
        tracker1RotQy = row[:,37]
        tracker1RotQz = row[:,38]
        tracker1RotQw = row[:,39]

        relativeHandRPosx = row[:,40]
        relativeHandRPosy = row[:,41]
        relativeHandRPosz = row[:,42]
        relativeHandLPosx = row[:,43]
        relativeHandLPosy = row[:,44]
        relativeHandLPosz = row[:,45]
        relativeTracker1Posx = row[:,46]
        relativeTracker1Posy = row[:,47]
        relativeTracker1Posz = row[:,48]

        if self.output_type=='euler':
            return (
                torch.FloatTensor(np.stack([headPosx, headPosy, headPosz, headRotx, headRoty, headRotz,
                    handRPosx, handRPosy, handRPosz, handRRotx, handRRoty, handRRotz,
                    handLPosx, handLPosy, handLPosz, handLRotx, handLRoty, handLRotz,
                    ],axis=-1)),
                torch.FloatTensor(np.stack([tracker1Posx, tracker1Posy, tracker1Posz, tracker1Rotx, tracker1Roty,
                    tracker1Rotz],axis=-1))
            )
        elif self.output_type=='quaternion':
            return (
                torch.FloatTensor(np.stack([headPosx, headPosy, headPosz, headRotQx, headRotQy, headRotQz, headRotQw,
                    handRPosx, handRPosy, handRPosz, handRRotQx, handRRotQy, handRRotQz, handRRotQw,
                    handLPosx, handLPosy, handLPosz, handLRotQx, handLRotQy, handLRotQz, handLRotQw,
                    ],axis=-1)),
                torch.FloatTensor(np.stack([tracker1Posx, tracker1Posy, tracker1Posz, tracker1RotQx, tracker1RotQy,
                    tracker1RotQz, tracker1RotQw],axis=-1))
            )
        elif self.output_type=='both':
            return (
                torch.FloatTensor(np.stack([headPosx, headPosy, headPosz, headRotx, headRoty, headRotz,headRotQx, headRotQy, headRotQz, headRotQw,
                    handRPosx, handRPosy, handRPosz, handRRotx, handRRoty, handRRotz, handRRotQx, handRRotQy, handRRotQz, handRRotQw,
                    handLPosx, handLPosy, handLPosz, handLRotx, handLRoty, handLRotz, handLRotQx, handLRotQy, handLRotQz, handLRotQw
                    ],axis=-1)),
                torch.FloatTensor(np.stack([tracker1Posx, tracker1Posy, tracker1Posz, tracker1Rotx, tracker1Roty,
                    tracker1Rotz, tracker1RotQx, tracker1RotQy, tracker1RotQz, tracker1RotQw],axis=-1))
            )
        elif self.output_type=='relative' or self.output_type=='relative_svm' or self.output_type=='hacklstm':
            return (
                torch.FloatTensor(np.stack([headPosy, headRotQx, headRotQy, headRotQz, headRotQw,
                    relativeHandRPosx, relativeHandRPosy, relativeHandRPosz, handRRotQx, handRRotQy, handRRotQz, handRRotQw,
                    relativeHandLPosx, relativeHandLPosy, relativeHandLPosz, handLRotQx, handLRotQy, handLRotQz, handLRotQw
                    ],axis=-1)),
                torch.FloatTensor(np.stack([relativeTracker1Posx, relativeTracker1Posy, relativeTracker1Posz,
                    tracker1RotQx, tracker1RotQy, tracker1RotQz, tracker1RotQw],axis=-1))
            )

class CSVDataset(torch.utils.data.Dataset):
    def __init__(self, root_path, output_type=Config['data_type']):
        files = os.listdir(root_path)
        files = [f for f in files if f.endswith('.csv')]
        all_data=[]
       
        for file in files:
            print(file)
            csv_data = pd.read_csv(os.path.join(root_path,file)).iloc[:,1:41]
            
            csv_data['relativeHandRPosx'] = csv_data.headPosx-csv_data.handRPosx
            csv_data['relativeHandRPosy'] = csv_data['headPosy']-csv_data['handRPosy']
            csv_data['relativeHandRPosz'] = csv_data['headPosz']-csv_data['handRPosz']
            csv_data['relativeHandLPosx'] = csv_data['headPosx']-csv_data['handLPosx']
            csv_data['relativeHandLPosy'] = csv_data['headPosy']-csv_data['handLPosy']
            csv_data['relativeHandLPosz'] = csv_data['headPosz']-csv_data['handLPosz']
            csv_data['relativeTracker1Posx'] = csv_data['headPosx']-csv_data['tracker1Posx']
            csv_data['relativeTracker1Posy'] = csv_data['headPosy']-csv_data['tracker1Posy']
            csv_data['relativeTracker1Posz'] = csv_data['headPosz']-csv_data['tracker1Posz']
            csv_data.to_csv('relative_columns.csv', index=False)
            data = np.array([csv_data])
            all_data.append(data)
        self.data = np.concatenate(all_data, axis=1).squeeze(0)
        self.scaler = MinMaxScaler(feature_range=(0,1))
        self.scaler.fit(self.data)
        self.scaled_data = self.scaler.transform(self.data)
        print(self.scaled_data.shape)

        self.output_type = output_type
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        keys = ['headPosx', 'headPosy', 'headPosz', 'headRotx', 'headRoty', 'headRotz', 'headRotQx', 'headRotQy', 'headRotQz', 'headRotQw', 'handRPosx', 'handRPosy', 'handRPosz', 'handRRotx', 'handRRoty', 'handRRotz', 'handRRotQx', 'handRRotQy', 'handRRotQz', 'handRRotQw', 'handLPosx', 'handLPosy', 'handLPosz', 'handLRotx', 'handLRoty', 'handLRotz', 'handLRotQx', 'handLRotQy', 'handLRotQz', 'handLRotQw', 'tracker1Posx', 'tracker1Posy', 'tracker1Posz', 'tracker1Rotx', 'tracker1Roty', 'tracker1Rotz', 'tracker1RotQx', 'tracker1RotQy', 'tracker1RotQz', 'tracker1RotQw', 'relativeHandRPosx', 'relativeHandRPosy', 'relativeHandRPosz', 'relativeHandLPosx', 'relativeHandLPosy', 'relativeHandLPosz', 'relativeTracker1Posx', 'relativeTracker1Posy', 'relativeTracker1Posz']
        row = self.scaled_data[idx]
        # print(row)
        # print(keys.index('headPosx'))
        headPosx = row[keys.index('headPosx')]
        headPosy = row[keys.index('headPosy')]
        headPosz = row[keys.index('headPosz')]
        headRotx = row[keys.index('headRotx')]
        headRoty = row[keys.index('headRoty')]
        headRotz = row[keys.index('headRotz')]
        headRotQx = row[keys.index('headRotQx')]
        headRotQy = row[keys.index('headRotQy')]
        headRotQz = row[keys.index('headRotQz')]
        headRotQw = row[keys.index('headRotQw')]

        handRPosx = row[keys.index('handRPosx')]
        handRPosy = row[keys.index('handRPosy')]
        handRPosz = row[keys.index('handRPosz')]
        handRRotx = row[keys.index('handRRotx')]
        handRRoty = row[keys.index('handRRoty')]
        handRRotz = row[keys.index('handRRotz')]
        handRRotQx = row[keys.index('handRRotQx')]
        handRRotQy = row[keys.index('handRRotQy')]
        handRRotQz = row[keys.index('handRRotQz')]
        handRRotQw = row[keys.index('handRRotQw')]

        handLPosx = row[keys.index('handLPosx')]
        handLPosy = row[keys.index('handLPosy')]
        handLPosz = row[keys.index('handLPosz')]
        handLRotx = row[keys.index('handLRotx')]
        handLRoty = row[keys.index('handLRoty')]
        handLRotz = row[keys.index('handLRotz')]
        handLRotQx = row[keys.index('handLRotQx')]
        handLRotQy = row[keys.index('handLRotQy')]
        handLRotQz = row[keys.index('handLRotQz')]
        handLRotQw = row[keys.index('handLRotQw')]

        tracker1Posx = row[keys.index('tracker1Posx')]
        tracker1Posy = row[keys.index('tracker1Posy')]
        tracker1Posz = row[keys.index('tracker1Posz')]
        tracker1Rotx = row[keys.index('tracker1Rotx')]
        tracker1Roty = row[keys.index('tracker1Roty')]
        tracker1Rotz = row[keys.index('tracker1Rotz')]
        tracker1RotQx = row[keys.index('tracker1RotQx')]
        tracker1RotQy = row[keys.index('tracker1RotQy')]
        tracker1RotQz = row[keys.index('tracker1RotQz')]
        tracker1RotQw = row[keys.index('tracker1RotQw')]

        relativeHandRPosx = row[keys.index('relativeHandRPosx')]
        relativeHandRPosy = row[keys.index('relativeHandRPosy')]
        relativeHandRPosz = row[keys.index('relativeHandRPosz')]
        relativeHandLPosx = row[keys.index('relativeHandLPosx')]
        relativeHandLPosy = row[keys.index('relativeHandLPosy')]
        relativeHandLPosz = row[keys.index('relativeHandLPosz')]
        relativeTracker1Posx = row[keys.index('relativeTracker1Posx')]
        relativeTracker1Posy = row[keys.index('relativeTracker1Posy')]
        relativeTracker1Posz = row[keys.index('relativeTracker1Posz')]


        if self.output_type=='euler':
            return (
                torch.FloatTensor([headPosx, headPosy, headPosz, headRotx, headRoty, headRotz,
                    handRPosx, handRPosy, handRPosz, handRRotx, handRRoty, handRRotz,
                    handLPosx, handLPosy, handLPosz, handLRotx, handLRoty, handLRotz,
                    ]),
                torch.FloatTensor([tracker1Posx, tracker1Posy, tracker1Posz, tracker1Rotx, tracker1Roty, 
                    tracker1Rotz])
            )
        elif self.output_type=='quaternion':
            return (
                torch.FloatTensor([headPosx, headPosy, headPosz, headRotQx, headRotQy, headRotQz, headRotQw,
                    handRPosx, handRPosy, handRPosz, handRRotQx, handRRotQy, handRRotQz, handRRotQw,
                    handLPosx, handLPosy, handLPosz, handLRotQx, handLRotQy, handLRotQz, handLRotQw,
                    ]),
                torch.FloatTensor([tracker1Posx, tracker1Posy, tracker1Posz, tracker1RotQx, tracker1RotQy, 
                    tracker1RotQz, tracker1RotQw])
            )
        elif self.output_type=='both':
            return (
                torch.FloatTensor([headPosx, headPosy, headPosz, headRotx, headRoty, headRotz,headRotQx, headRotQy, headRotQz, headRotQw,
                    handRPosx, handRPosy, handRPosz, handRRotx, handRRoty, handRRotz, handRRotQx, handRRotQy, handRRotQz, handRRotQw,
                    handLPosx, handLPosy, handLPosz, handLRotx, handLRoty, handLRotz, handLRotQx, handLRotQy, handLRotQz, handLRotQw
                    ]),
                torch.FloatTensor([tracker1Posx, tracker1Posy, tracker1Posz, tracker1Rotx, tracker1Roty, 
                    tracker1Rotz, tracker1RotQx, tracker1RotQy, tracker1RotQz, tracker1RotQw])
            )
        elif self.output_type=='relative' or self.output_type=='relative_svm':
            # return (
            #     torch.FloatTensor([headPosy, headRotx, headRoty, headRotz,
            #         relativeHandRPosx, relativeHandRPosy, relativeHandRPosz, handRRotx, handRRoty, handRRotz,
            #         relativeHandLPosx, relativeHandLPosy, relativeHandLPosz, handLRotx, handLRoty, handLRotz,
            #         ]),
            #     torch.FloatTensor([relativeTracker1Posx, relativeTracker1Posy, relativeTracker1Posz,
            #         tracker1Rotx, tracker1Roty, tracker1Rotz])
            # )
            return (
                torch.FloatTensor(np.stack([headPosy, headRotQx, headRotQy, headRotQz, headRotQw,
                    relativeHandRPosx, relativeHandRPosy, relativeHandRPosz, handRRotQx, handRRotQy, handRRotQz, handRRotQw,
                    relativeHandLPosx, relativeHandLPosy, relativeHandLPosz, handLRotQx, handLRotQy, handLRotQz, handLRotQw
                    ],axis=-1)),
                torch.FloatTensor(np.stack([relativeTracker1Posx, relativeTracker1Posy, relativeTracker1Posz, #],axis=-1))
                    tracker1RotQx, tracker1RotQy, tracker1RotQz, tracker1RotQw],axis=-1))
            )

class GestureCSVDataset(torch.utils.data.Dataset):
    def __init__(self, root_path, output_type=Config['data_type']):
        files = os.listdir(root_path)
        files = [f for f in files if f.endswith('.csv')]
        all_data = []

        for file in files:
            csv_data = pd.read_csv(os.path.join(root_path, file))
            for i in range(0, 10):
                i = str(i)
                csv_data['relativeHandRPosx' + i] = csv_data['headPosx' + i] - csv_data['handRPosx' + i]
                csv_data['relativeHandRPosy' + i] = csv_data['headPosy' + i] - csv_data['handRPosy' + i]
                csv_data['relativeHandRPosz' + i] = csv_data['headPosz' + i] - csv_data['handRPosz' + i]
                csv_data['relativeHandLPosx' + i] = csv_data['headPosx' + i] - csv_data['handLPosx' + i]
                csv_data['relativeHandLPosy' + i] = csv_data['headPosy' + i] - csv_data['handLPosy' + i]
                csv_data['relativeHandLPosz' + i] = csv_data['headPosz' + i] - csv_data['handLPosz' + i]
            all_data.append(csv_data)
        # Concatenate all data
        self.data = pd.concat(all_data, axis=0, ignore_index=True)
        # Pull out the string gestures before scaling
        gestures = self.data['gesture'].astype('category')
        self.data = self.data.drop(columns='gesture')
        # Scale
        self.scaler = MinMaxScaler(feature_range=(-1, 1))
        self.scaler.fit(self.data)
        self.scaled_data = self.scaler.transform(self.data)
        # Put back the gestures/labels and add column names for easier access in __getitem__
        self.labels = dict(enumerate(gestures.cat.categories))
        self.scaled_data = np.append(self.scaled_data, np.reshape(gestures.cat.codes.values, (-1, 1)), 1)
        self.scaled_data = pd.DataFrame(self.scaled_data,
                                        columns=pd.Index(np.append(self.data.columns.values, 'gesture')))
        self.output_type = output_type

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        row = self.scaled_data.iloc[idx]

        label = row['gesture']

        relativeHandRPos = []
        relativeHandLPos = []
        headRot = []
        handRRot = []
        handLRot = []
        for i in range(0, 10):
            i = str(i)
            relativeHandRPos.append(row['relativeHandRPosx' + i])
            relativeHandRPos.append(row['relativeHandRPosy' + i])
            relativeHandRPos.append(row['relativeHandRPosz' + i])
            relativeHandLPos.append(row['relativeHandLPosx' + i])
            relativeHandLPos.append(row['relativeHandLPosy' + i])
            relativeHandLPos.append(row['relativeHandLPosz' + i])
            headRot.append(row['headRotx' + i])
            headRot.append(row['headRoty' + i])
            headRot.append(row['headRotz' + i])
            handRRot.append(row['handRRotx' + i])
            handRRot.append(row['handRRoty' + i])
            handRRot.append(row['handRRotz' + i])
            handLRot.append(row['handLRotx' + i])
            handLRot.append(row['handLRoty' + i])
            handLRot.append(row['handLRotz' + i])

        if self.output_type == 'gesture':
            return (
                torch.FloatTensor(relativeHandRPos + relativeHandLPos + headRot + handRRot + handLRot),
                torch.tensor(label, dtype=torch.int64)
            )

class GestureCSVDatasetv2(torch.utils.data.Dataset):
    def __init__(self, root_path, output_type='quaternion', look_back=10, step_value=1):
        files = os.listdir(root_path)
        files = [f for f in files if f.endswith('.csv')]
        self.stats = {
            'up': 0,
            'down': 0,
            'forward': 0,
            'backward': 0,
            'none': 0
        }
        gestures = []
        for file in files:
            csv_data = pd.read_csv(os.path.join(root_path, file))
            up_gestures_idx = csv_data[csv_data['gesture'].isin(['Up','Up0'])].index.to_numpy()
            down_gestures_idx = csv_data[csv_data['gesture'].isin(['Down','Down0'])].index.to_numpy()
            forward_gestures_idx = csv_data[csv_data['gesture'].isin(['Forward','Forward0'])].index.to_numpy()
            backward_gestures_idx = csv_data[csv_data['gesture'].isin(['Backward','Backward0'])].index.to_numpy()
            gestures_idx = np.concatenate(
                [up_gestures_idx, down_gestures_idx, forward_gestures_idx, backward_gestures_idx])
            #             print(gestures_idx.shape)

            csv_data['relativeHandRPosx'] = csv_data['headPosx'] - csv_data['handRPosx']
            csv_data['relativeHandRPosy'] = csv_data['headPosy'] - csv_data['handRPosy']
            csv_data['relativeHandRPosz'] = csv_data['headPosz'] - csv_data['handRPosz']
            csv_data['relativeHandLPosx'] = csv_data['headPosx'] - csv_data['handLPosx']
            csv_data['relativeHandLPosy'] = csv_data['headPosy'] - csv_data['handLPosy']
            csv_data['relativeHandLPosz'] = csv_data['headPosz'] - csv_data['handLPosz']
            #             csv_data['relativeTracker1Posx'] = csv_data['headPosx']-csv_data['tracker1Posx']
            #             csv_data['relativeTracker1Posy'] = csv_data['headPosy']-csv_data['tracker1Posy']
            #             csv_data['relativeTracker1Posz'] = csv_data['headPosz']-csv_data['tracker1Posz']
            fields = set(csv_data.keys())
            needed_feats = []
            if output_type == 'quaternion':
                needed_feats = ['headPosy', 'headRotQx', 'headRotQy', 'headRotQz', 'headRotQw',
                                'relativeHandRPosx', 'relativeHandRPosy', 'relativeHandRPosz', 'handRRotQx',
                                'handRRotQy', 'handRRotQz', 'handRRotQw',
                                'relativeHandLPosx', 'relativeHandLPosy', 'relativeHandLPosz', 'handLRotQx',
                                'handLRotQy', 'handLRotQz', 'handLRotQw']
            remove_fields = list(fields - set(needed_feats))
            for field in remove_fields:
                csv_data = csv_data.drop(columns=[field])
            #             print(fields)
            data = np.array([csv_data]).squeeze(0)
            #             print(data.shape)
            scaler = MinMaxScaler(feature_range=(-1, 1))
            scaler.fit(data)
            scaled_data = scaler.transform(data)
            # lstm_data = []
            print()
            for i in range(len(scaled_data) - look_back - 1):
                a = scaled_data[i:(i + look_back):step_value]
                if self.check_proximal_gesture_type(i, up_gestures_idx):
                    gestures.append((a, 1))
                    self.stats['up'] += 1
                elif self.check_proximal_gesture_type(i, down_gestures_idx):
                    gestures.append((a, 2))
                    self.stats['down'] += 1
                elif self.check_proximal_gesture_type(i, forward_gestures_idx):
                    gestures.append((a, 3))
                    self.stats['forward'] += 1
                elif self.check_proximal_gesture_type(i, backward_gestures_idx):
                    gestures.append((a, 4))
                    self.stats['backward'] += 1
                else:
                    gestures.append((a, 0))
                    self.stats['none'] += 1
                # lstm_data.append(a)
        self.gestures = gestures

    def __len__(self):
        return len(self.gestures)

    def __getitem__(self, idx):
        sequence, label = self.gestures[idx]
        # print(len(self.gestures[idx]), sequence.shape, label)
        return torch.FloatTensor(sequence), torch.ones(1)*label

    def check_proximal_gesture_type(self, idx, gestures_idx, thresh=10):
        for jdx in gestures_idx:
            if abs(idx - jdx) < thresh:
                return True
        return False

class GrabCSVDataset(torch.utils.data.Dataset):
    def __init__(self, root_path, output_type=Config['data_type']):
        files = os.listdir(root_path)
        files = [f for f in files if f.endswith('.csv')]
        all_data = []


        for file in files:
            print(file)
            csv_data = pd.read_csv(os.path.join(root_path, file))

            csv_data['relativeHandRPosx'] = csv_data['headPosx'] - csv_data['handRPosx']
            csv_data['relativeHandRPosy'] = csv_data['headPosy'] - csv_data['handRPosy']
            csv_data['relativeHandRPosz'] = csv_data['headPosz'] - csv_data['handRPosz']
            csv_data['relativeHandLPosx'] = csv_data['headPosx'] - csv_data['handLPosx']
            csv_data['relativeHandLPosy'] = csv_data['headPosy'] - csv_data['handLPosy']
            csv_data['relativeHandLPosz'] = csv_data['headPosz'] - csv_data['handLPosz']
            csv_data['relativeTracker1Posx'] = csv_data['headPosx'] - csv_data['tracker1Posx']
            csv_data['relativeTracker1Posy'] = csv_data['headPosy'] - csv_data['tracker1Posy']
            csv_data['relativeTracker1Posz'] = csv_data['headPosz'] - csv_data['tracker1Posz']

            rowsPerGrab = 0
            grabIndices = csv_data.index[
                csv_data['gesture'] != "None"].tolist()  # find indices of rows that represent the end of a gesture
            for i in range(len(grabIndices)):
                csv_data.iloc[(grabIndices[i] - rowsPerGrab): grabIndices[i]]['gesture'] = csv_data.iloc[grabIndices[i]]['gesture']
                all_data.append(csv_data.iloc[(grabIndices[i] - rowsPerGrab): grabIndices[i] + 1])
        #print(len(grabIndices))
        #print(len(all_data))
        #for i in all_data:
            #print(i['gesture'])
        numRows = 0;
        for i in all_data:
            numRows += len(i)
        print(numRows)
        # Concatenate all data
        self.data = pd.concat(all_data, axis=0, ignore_index=True)
        #print(len(self.data))
        # Pull out the string gestures before scaling
        gestures = self.data['gesture'].astype('category')
        self.data = self.data.drop(columns='gesture')
        # Scale
        self.scaler = MinMaxScaler(feature_range=(-1, 1))
        self.scaler.fit(self.data)
        self.scaled_data = self.scaler.transform(self.data)
        self.features = self.data.columns.values
        # Put back the gestures/labels and add column names for easier access in __getitem__
        self.labels = dict(enumerate(gestures.cat.categories))
        self.scaled_data = np.append(self.scaled_data, np.reshape(gestures.cat.codes.values, (-1, 1)), 1)
        self.scaled_data = pd.DataFrame(self.scaled_data,
                                        columns=pd.Index(np.append(self.data.columns.values, 'gesture')))
        self.output_type = output_type

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        keys = ['timestamp','headPosx', 'headPosy', 'headPosz', 'headRotx', 'headRoty', 'headRotz', 'headRotQx', 'headRotQy', 'headRotQz', 'headRotQw', 'handRPosx', 'handRPosy', 'handRPosz', 'handRRotx', 'handRRoty', 'handRRotz', 'handRRotQx', 'handRRotQy', 'handRRotQz', 'handRRotQw', 'handLPosx', 'handLPosy', 'handLPosz', 'handLRotx', 'handLRoty', 'handLRotz', 'handLRotQx', 'handLRotQy', 'handLRotQz', 'handLRotQw', 'tracker1Posx', 'tracker1Posy', 'tracker1Posz', 'tracker1Rotx', 'tracker1Roty', 'tracker1Rotz', 'tracker1RotQx', 'tracker1RotQy', 'tracker1RotQz', 'tracker1RotQw', 'gesture', 'relativeHandRPosx', 'relativeHandRPosy', 'relativeHandRPosz', 'relativeHandLPosx', 'relativeHandLPosy', 'relativeHandLPosz', 'relativeTracker1Posx', 'relativeTracker1Posy', 'relativeTracker1Posz']
        row = self.scaled_data.iloc[idx]
        #label = row[keys.index('gesture')]
        label = row['gesture']

        timestamp = row[keys.index('timestamp')]
        headPosx = row['headPosx']
        headPosy = row['headPosy']
        headPosz = row['headPosz']

        headRotQx = row['headRotQx']
        headRotQy = row['headRotQy']
        headRotQz = row['headRotQz']
        headRotQw = row['headRotQw']


        handRRotQx = row['handRRotQx']
        handRRotQy = row['handRRotQy']
        handRRotQz = row['handRRotQz']
        handRRotQw = row['handRRotQw']


        handLRotQx = row['handLRotQx']
        handLRotQy = row['handLRotQy']
        handLRotQz = row['handLRotQz']
        handLRotQw = row['handLRotQw']


        tracker1RotQx = row['tracker1RotQx']
        tracker1RotQy = row['tracker1RotQy']
        tracker1RotQz = row['tracker1RotQz']
        tracker1RotQw = row['tracker1RotQw']

        relativeHandRPosx = row['relativeHandRPosx']
        relativeHandRPosy = row['relativeHandRPosy']
        relativeHandRPosz = row['relativeHandRPosz']
        relativeHandLPosx = row['relativeHandLPosx']
        relativeHandLPosy = row['relativeHandLPosy']
        relativeHandLPosz = row['relativeHandLPosz']
        relativeTracker1Posx = row['relativeTracker1Posx']
        relativeTracker1Posy = row['relativeTracker1Posy']
        relativeTracker1Posz = row['relativeTracker1Posz']


        if self.output_type == 'grab':
            return (
                    torch.FloatTensor([headPosx, headPosy, headPosz, headRotQx, headRotQy, headRotQz, headRotQw,
                    relativeHandRPosx, relativeHandRPosy, relativeHandRPosz, handRRotQx, handRRotQy, handRRotQz, handRRotQw,
                    relativeHandLPosx, relativeHandLPosy, relativeHandLPosz, handLRotQx, handLRotQy, handLRotQz, handLRotQw,
                    relativeTracker1Posx, relativeTracker1Posy, relativeTracker1Posz, tracker1RotQx, tracker1RotQy, tracker1RotQz, tracker1RotQw]),

                    torch.tensor(label, dtype=torch.int64)
            )


class NumpadTypingCSVDataset(torch.utils.data.Dataset):
    def __init__(self, root_path, data_type):
        self.data_type = data_type
        files = os.listdir(root_path)
        files = [f for f in files if f.endswith('.csv')]
        all_data = []

        for file in files:
            csv_data = pd.read_csv(os.path.join(root_path, file)).iloc[:,1:32]
            csv_data['relativeHandRPosx'] = csv_data['headPosx'] - csv_data['handRPosx']
            csv_data['relativeHandRPosy'] = csv_data['headPosy'] - csv_data['handRPosy']
            csv_data['relativeHandRPosz'] = csv_data['headPosz'] - csv_data['handRPosz']
            csv_data['relativeHandLPosx'] = csv_data['headPosx'] - csv_data['handLPosx']
            csv_data['relativeHandLPosy'] = csv_data['headPosy'] - csv_data['handLPosy']
            csv_data['relativeHandLPosz'] = csv_data['headPosz'] - csv_data['handLPosz']
            all_data.append(csv_data)
        # Concatenate all data
        self.data = pd.concat(all_data, axis=0, ignore_index=True)
        # Only look at start and end position sample for now
        end_mask = (self.data['key'].shift(-1) == -1)
        start_mask = (self.data['key'].shift(1) == -1)
        end_data = self.data[end_mask]
        start_data = self.data[start_mask]
        end_data = end_data[end_data['key'] != -1].reset_index(drop=True)
        start_data = start_data[start_data['key'] != -1].reset_index(drop=True)
        if data_type == "end":
            self.data = end_data
            keys = self.data['key'].astype('category')
            self.data = self.data.drop(columns=['key'])
        else:
            self.data = start_data.join(end_data, lsuffix="_start", rsuffix="_end")
            # Pull out the string gestures before scaling
            keys = self.data['key_start'].astype('category')
            self.data = self.data.drop(columns=['key_start','key_end'])
        # Scale
        self.scaler = MinMaxScaler(feature_range=(-1, 1))
        self.scaler.fit(self.data)
        self.scaled_data = self.scaler.transform(self.data)
        self.features = self.data.columns.values
        # Put back the gestures/labels and add column names for easier access in __getitem__
        self.labels = dict(enumerate(keys.cat.categories))
        self.scaled_data = np.append(self.scaled_data, np.reshape(keys.cat.codes.values, (-1, 1)), 1)
        self.scaled_data = pd.DataFrame(self.scaled_data,
                                        columns=pd.Index(np.append(self.data.columns.values, 'key')))

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        row = self.scaled_data.iloc[idx]

        label = row['key']

        if self.data_type == 'end':
            return (
                torch.FloatTensor([
                    row['relativeHandRPosx'],
                    row['relativeHandRPosy'],
                    row['relativeHandRPosz'],
                    row['relativeHandLPosx'],
                    row['relativeHandLPosy'],
                    row['relativeHandLPosz'],
                    row['headRotx'],
                    row['headRoty'],
                    row['headRotz'],
                    row['handRRotx'],
                    row['handRRoty'],
                    row['handRRotz'],
                    row['handLRotx'],
                    row['handLRoty'],
                    row['handLRotz'],
                ]),
                torch.tensor(label, dtype=torch.int64)
            )
        else:
            return (
                torch.FloatTensor([
                    row['relativeHandRPosx_start'],
                    row['relativeHandRPosy_start'],
                    row['relativeHandRPosz_start'],
                    row['relativeHandLPosx_start'],
                    row['relativeHandLPosy_start'],
                    row['relativeHandLPosz_start'],
                    row['headRotx_start'],
                    row['headRoty_start'],
                    row['headRotz_start'],
                    row['handRRotx_start'],
                    row['handRRoty_start'],
                    row['handRRotz_start'],
                    row['handLRotx_start'],
                    row['handLRoty_start'],
                    row['handLRotz_start'],
                    row['relativeHandRPosx_end'],
                    row['relativeHandRPosy_end'],
                    row['relativeHandRPosz_end'],
                    row['relativeHandLPosx_end'],
                    row['relativeHandLPosy_end'],
                    row['relativeHandLPosz_end'],
                    row['headRotx_end'],
                    row['headRoty_end'],
                    row['headRotz_end'],
                    row['handRRotx_end'],
                    row['handRRoty_end'],
                    row['handRRotz_end'],
                    row['handLRotx_end'],
                    row['handLRoty_end'],
                    row['handLRotz_end'],
                ]),
                torch.tensor(label, dtype=torch.int64)
            )

class TypingCSVDataset(torch.utils.data.Dataset):
    def __init__(self, root_path, data_type, hand):
        self.data_type = data_type
        self.hand = hand
        files = os.listdir(root_path)
        files = [f for f in files if f.endswith('.csv')]
        all_data = []

        for file in files:
            csv_data = pd.read_csv(os.path.join(root_path, file)).iloc[:,1:33]
            csv_data['relativeHandRPosx'] = csv_data['headPosx'] - csv_data['handRPosx']
            csv_data['relativeHandRPosy'] = csv_data['headPosy'] - csv_data['handRPosy']
            csv_data['relativeHandRPosz'] = csv_data['headPosz'] - csv_data['handRPosz']
            csv_data['relativeHandLPosx'] = csv_data['headPosx'] - csv_data['handLPosx']
            csv_data['relativeHandLPosy'] = csv_data['headPosy'] - csv_data['handLPosy']
            csv_data['relativeHandLPosz'] = csv_data['headPosz'] - csv_data['handLPosz']
            all_data.append(csv_data)
        # Concatenate all data
        self.data = pd.concat(all_data, axis=0, ignore_index=True)
        # Only look at start and end position sample for now
        end_mask = (self.data['key'].shift(-1) == "none")
        end_data = self.data[end_mask]
        hand_mask = (end_data['hand'] == hand)
        end_data = end_data[hand_mask]
        end_data = end_data[end_data['key'] != "none"].reset_index(drop=True)
        self.data = end_data
        keys = self.data['key'].astype('category')
        self.data = self.data.drop(columns=['key', 'hand'])
        # Scale
        self.scaler = MinMaxScaler(feature_range=(-1, 1))
        self.scaler.fit(self.data)
        self.scaled_data = self.scaler.transform(self.data)
        self.features = self.data.columns.values
        # Put back the gestures/labels and add column names for easier access in __getitem__
        self.labels = dict(enumerate(keys.cat.categories))
        self.scaled_data = np.append(self.scaled_data, np.reshape(keys.cat.codes.values, (-1, 1)), 1)
        self.scaled_data = pd.DataFrame(self.scaled_data,
                                        columns=pd.Index(np.append(self.data.columns.values, 'key')))

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        row = self.scaled_data.iloc[idx]

        label = row['key']

        if self.hand == "left":
            return (
               torch.FloatTensor([
                   row['relativeHandLPosx'],
                   row['relativeHandLPosy'],
                   row['relativeHandLPosz'],
                   row['headRotx'],
                   row['headRoty'],
                   row['headRotz'],
                   row['handLRotx'],
                   row['handLRoty'],
                   row['handLRotz']
               ]),
               torch.tensor(label, dtype=torch.int64)
            )
        else:
            return (
                torch.FloatTensor([
                    row['relativeHandRPosx'],
                    row['relativeHandRPosy'],
                    row['relativeHandRPosz'],
                    row['headRotx'],
                    row['headRoty'],
                    row['headRotz'],
                    row['handRRotx'],
                    row['handRRoty'],
                    row['handRRotz']
                ]),
                torch.tensor(label, dtype=torch.int64)
            )
