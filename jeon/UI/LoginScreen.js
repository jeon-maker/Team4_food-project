import React, { Component } from "react";
import { View, Text, Button, StyleSheet, TextInput } from 'react-native';
import firestore , { doc  } from '@react-native-firebase/firestore';
import style from "./style";

export default class LoginScreen extends Component {
    state = {
        id: '',
        id_list:[],
        pw:'',
        pw_list:[],
        prevID: null
    }

    

    onChageID = (event) =>{
        this.setState({
            id: event
        })
    }

    onChangePW = (event) =>{
        this.setState({
            pw : event
        })
    }

    onLogin = ()=>{ 
        this.setState(prevState=>{
            const db = firestore().collection('Members');
            db.doc(prevState.id).get().then((doc)=>{
                //id가 존재하지 않으면 없는 id라는 경고문
                //id는 존재하는데 pw가 틀리면 pw가 틀렸다는 경고문
                //id 존재하고 pw 일치하면 로그인 성공
                if(!doc.exists){
                    alert("존재하지 않는 ID 입니다")
                }else if(doc.exists & (prevState.id == doc.data().ID & prevState.pw != doc.data().PW))
                {alert("비밀번호가 틀렸습니다")}
                else if(doc.exists & (prevState.id ==doc.data().ID & prevState.pw == doc.data().PW)){
                    alert("로그인 성공!");
                    this.props.navigation.navigate('Main2',{prevID : this.state.id});
                }
            })
        })
    }

    render() {
        return (
            <View style={style.container}>
                <Text style={{ fontSize: 30 }}>Login Screen</Text>
                <TextInput
                    style={style.input}
                    onChangeText={this.onChageID}
                    placeholder="ID"
                    value={this.state.id}
                />
                <TextInput
                    style={style.input}
                    onChangeText={this.onChangePW}
                    placeholder="PW"
                    value={this.state.pw}
                />
                <Button color={style.Button.color} backgroundColor={style.Button.backgroundColor} title ="로그인" onPress={this.onLogin}/>
                <Button color={style.Button.color} backgroundColor={style.Button.backgroundColor} onPress={() => this.gotoStartScreen()} title='back to Start' />
            </View>
        )
    }
    gotoStartScreen() {
        this.props.navigation.navigate('Start')
    }
}

