import React, { Component } from "react";
import { View, Text, Button, StyleSheet } from 'react-native';
import style from "./style";

export default class Main2Screen extends Component {
    render() {
        return (
            <View style={style.container}>
                <Text style={style.text}>Team 4 Project</Text>
                <Text style={style.text}>Diet management</Text>
                <Text></Text>
                <Text></Text>
                <Text></Text>
                <Text></Text>
                <Text></Text>
                <Text></Text>
                <Text></Text>
                <Text></Text>
                <View style={[{ width: "100%"} ]}>
                <Text style={style.text}>식단 관리 달력 넣기</Text>
                <Text style={style.text}>하루 식단 기록하기</Text>
                <Button color={style.Button.color} title="사진찍어 식단 칼로리 측정하기"  />

                </View>
            </View >

        )
    }
   
}