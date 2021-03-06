using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Serialization;
using UnityEngine.XR.Interaction.Toolkit;

[RequireComponent(typeof(XRGrabInteractable))]
public class VES_MaterialPropertyBlockHelper : MonoBehaviour
{
    public Renderer[] myRenderers;
    public Color ActiveColor; 
    public MaterialPropertyBlock _activatedMBP;
    public MaterialPropertyBlock _deactivatedMBP;
    public MaterialPropertyBlock originalMBP;
    
    void OnEnable()
    {
    }

    private void OnDisable()
    {
    }

    void Start()
    {
        //var test = this.GetComponents(_myOutlines);
        myRenderers = this.GetComponentsInChildren<Renderer>(true);
        originalMBP = new MaterialPropertyBlock();
         _activatedMBP = new MaterialPropertyBlock();
         _deactivatedMBP = new MaterialPropertyBlock();
        // _activatedMBP.SetColor("_BaseColor", new Color(0, 116, 221, 255));
        // _deactivatedMBP.SetColor("_BaseColor", new Color(221, 0, 0, 255));
    }

    private Color color1 = new Color(0, 62, 192, 255);
    private Color color2 = new Color(255, 0, 0, 255);
    
    public void HandleVisualChange(bool b)
    {
        if (myRenderers.Length > 0)
        {
            foreach (var r in myRenderers)
            {
                if (b)
                {
                    //r.material.color = color1;
                    r.material.SetColor("_BaseColor", color1);
                    // foreach (var m in r.materials)
                    // {
                    //     m.SetColor("_BaseColor", new Color(0, 116, 221, 255));
                    // }
                    // print(r.HasPropertyBlock());
                    // r.GetPropertyBlock(originalMBP);
                    // r.GetPropertyBlock(_activatedMBP);
                    // print(originalMBP.GetColor(1));
                    // _activatedMBP.SetColor("_BaseColor", new Color(0, 116, 221, 255));
                    // r.SetPropertyBlock(_activatedMBP);    
                }
                else
                {
//                    r.material.color = color2;
                    r.material.SetColor("_BaseColor", color2);
                    // foreach (var m in r.materials)
                    // {
                    //     m.SetColor("_BaseColor", new Color(255, 0, 0, 255));
                    // }
                    // print(r.HasPropertyBlock());
                    // r.GetPropertyBlock(originalMBP);
                    // r.GetPropertyBlock(_deactivatedMBP);
                    // _deactivatedMBP.SetColor("_BaseColor", new Color(0, 0, 0, 0));
                    // r.SetPropertyBlock(_deactivatedMBP);
                }
            }
        }
        else
        {
            Dev.LogError("Where is " + this.name + "'s renderer");
        }
    }
}